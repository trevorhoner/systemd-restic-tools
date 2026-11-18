#!/usr/bin/env bash
# ~/.local/bin/restic-auto.sh
# chmod +x ~/.local/bin/restic-auto.sh

set -u

# ─── Common settings ────────────────────────────────────────────────
PASSFILE="$HOME/.bashscripts/.restic-passphrase"
SOURCE="$HOME/"
TAGS="--tag arch-home --tag $(date +%Y-%m)"

# ─── Home Backups ───────────────────────────────────────────────────
EXTERNAL_REPO="/mnt/ExternalDrive/restic"
EXTERNAL_LOG="$HOME/.log/restic-external.log"
EXTERNAL_EXCLUDES=(
    "$HOME/.cache"
    "$HOME/Downloads"
    "$HOME/.local/share/Trash"
    "$HOME/.npm"
    "$HOME/.cargo"
)

CLOUD_REPO="de4875@de48975.rsync.net:restic"
CLOUD_LOG="$HOME/.log/restic-cloud.log"
CLOUD_EXCLUDES=(
    "$HOME/.cache"
    "$HOME/Downloads"
    "$HOME/Games"
    "$HOME/Videos"
    "$HOME/.local/share/Trash"
    "$HOME/.npm"
    "$HOME/.cargo"
)

# ─── Log Logic ──────────────────────────────────────────────────────
ALL_LOGS=("$EXTERNAL_LOG" "$CLOUD_LOG")

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] ${1:-}"
    if $VERBOSE; then
        echo "$msg" >&2
    fi
    echo "$msg" | tee -a "${ALL_LOGS[@]}" 2>/dev/null
}

# ─── Verbose Option ─────────────────────────────────────────────────
VERBOSE=false
if [[ "${1:-}" == "--verbose" || "${1:-}" == "-v" ]]; then
    VERBOSE=true
    shift
fi

log "Starting restic backups"

# ─── Lock to prevent overlapping runs ───────────────────────────────
LOCK="/tmp/restic-backup.lock"
if [[ -e "$LOCK" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Another instance running, exiting" | tee -a "${ALL_LOGS[@]}" 2>/dev/null
    exit 1
fi
trap 'rm -f "$LOCK"' EXIT
touch "$LOCK"

# ─── Backup & Prune Function ────────────────────────────────────────
backup_and_prune() {
    local repo="${1:-}"
    local logfile="$2"
    local source_path="$3"
    shift 3

    local sudo_cmd=""
    if [[ "${1:-}" == "--sudo" ]]; then
        sudo_cmd="sudo"
        shift
    fi

    local excludes=("$@")

    if $VERBOSE; then
        echo "→ Starting backup of $source_path to $repo" >&2
    fi

    # === Backup ===
    if $VERBOSE; then
        $sudo_cmd restic -r "$repo" backup \
            --password-file "$PASSFILE" \
            --verbose \
            --exclude-caches \
            "${excludes[@]/#/--exclude=}" \
            $TAGS \
            "$source_path" 2>&1 | tee -a "$logfile"
    else
        $sudo_cmd restic -r "$repo" backup \
            --password-file "$PASSFILE" \
            --exclude-caches \
            "${excludes[@]/#/--exclude=}" \
            $TAGS \
            "$source_path" >> "$logfile" 2>&1
    fi

    local backup_status=$?

    # === Prune ===
    if $VERBOSE; then
        $sudo_cmd restic -r "$repo" \
            --password-file "$PASSFILE" \
            --verbose \
            forget --prune \
            --keep-hourly 24 \
            --keep-daily 7 \
            --keep-weekly 4 \
            --keep-monthly 12 \
            --keep-yearly 2 2>&1 | tee -a "$logfile"
    else
        $sudo_cmd restic -r "$repo" \
            --password-file "$PASSFILE" \
            forget --prune \
            --keep-hourly 24 \
            --keep-daily 7 \
            --keep-weekly 4 \
            --keep-monthly 12 \
            --keep-yearly 2 >> "$logfile" 2>&1
    fi

    local prune_status=$?

    # === Final status ===
    if (( backup_status == 0 || backup_status == 3 )) && (( prune_status == 0 || prune_status == 3 )); then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $repo ($source_path) finished OK" >> "$logfile"
        if $VERBOSE; then
            echo "→ $repo ($source_path) finished OK" >&2
        fi
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Backup to $repo had issues (backup=$backup_status, prune=$prune_status)" >> "$logfile"
        if $VERBOSE; then
            echo "→ Backup to $repo had issues (backup=$backup_status, prune=$prune_status)" >&2
        fi
    fi
}

# ─── Execute Backups ────────────────────────────────────────────────
backup_and_prune "$EXTERNAL_REPO" "$EXTERNAL_LOG" "$SOURCE" "${EXTERNAL_EXCLUDES[@]}"
backup_and_prune "$CLOUD_REPO" "$CLOUD_LOG" "$SOURCE" "${CLOUD_EXCLUDES[@]}"

# Timeshift is disabled for now
#backup_and_prune "$EXTERNAL_TREPO" "$EXTERNAL_TLOG" "$T_SOURCE"
#backup_and_prune "$CLOUD_TREPO" "$CLOUD_TLOG" "$T_SOURCE"

log "All operations completed"
