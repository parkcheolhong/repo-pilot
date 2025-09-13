#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/setup.sh OWNER/REPO [REVIEWER_LOGIN]
REPO="${1:-}"
REVIEWER_LOGIN="${2:-}"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI (gh) is required. Install: https://cli.github.com/"
  exit 1
fi

if [[ -z "$REPO" ]]; then
  read -rp "Enter repo as OWNER/REPO: " REPO
fi

echo "==> Checking repo access for $REPO"
gh repo view "$REPO" >/dev/null

echo "==> Setting repo options"
gh repo edit "$REPO" \
  --default-branch main \
  --delete-branch-on-merge \
  --allow-update-branch \
  --enable-automated-security-fixes \
  --enable-vulnerability-alerts \
  --add-topic repo-pilot --add-topic templates || true

echo "==> Ensuring .github files exist (copying to a temp clone)"
tmpdir=$(mktemp -d)
git clone "https://github.com/$REPO.git" "$tmpdir"
mkdir -p "$tmpdir/.github/workflows"
rsync -a --exclude='.git' ".github/" "$tmpdir/.github/" || true
rsync -a --exclude='.git' "SECURITY.md" "$tmpdir/" || true
git -C "$tmpdir" add .
if ! git -C "$tmpdir" diff --cached --quiet; then
  git -C "$tmpdir" config user.name "repo-pilot"
  git -C "$tmpdir" config user.email "repo-pilot@example.com"
  git -C "$tmpdir" commit -m "chore(repo-pilot): add workflows, templates, labels, dependabot"
  git -C "$tmpdir" push origin HEAD:repo-pilot/bootstrap || true
  gh pr create --repo "$REPO" --base main --head repo-pilot/bootstrap \
    --title "chore(repo-pilot): bootstrap workflows & templates" \
    --body "Adds CI, labeler, templates, Dependabot, and protections."
else
  echo "No .github changes to commit."
fi

echo "==> Creating/Updating branch protection for 'main'"
# Note: required status checks must match job names: 'lint' and 'semantic-pr'
gh api -X PUT "repos/$REPO/branches/main/protection" \
  -H "Accept: application/vnd.github+json" \
  -F required_status_checks.strict=true \
  -F required_status_checks.contexts[]="lint" \
  -F required_status_checks.contexts[]="semantic-pr" \
  -F enforce_admins=true \
  -F required_pull_request_reviews.required_approving_review_count=1 \
  -F required_pull_request_reviews.dismiss_stale_reviews=true \
  -F required_pull_request_reviews.require_code_owner_reviews=false \
  -F restrictions= \
  -F allow_deletions=false \
  -F allow_force_pushes=false \
  -F required_linear_history=true \
  -F required_conversation_resolution=true

echo "==> Creating environments (staging, production)"
for env in staging production; do
  if [[ -n "$REVIEWER_LOGIN" ]]; then
    # Fetch reviewer ID for environment protection rule
    RID=$(gh api "users/$REVIEWER_LOGIN" --jq '.id')
    gh api -X PUT "repos/$REPO/environments/$env" \
      -H "Accept: application/vnd.github+json" \
      -f wait_timer=0 \
      -f deployment_branch_policy.custom_branch_policies=false \
      -f "reviewers[0][type]=User" \
      -f "reviewers[0][id]=$RID"
  else
    gh api -X PUT "repos/$REPO/environments/$env" \
      -H "Accept: application/vnd.github+json" \
      -f wait_timer=0 \
      -f deployment_branch_policy.custom_branch_policies=false
  fi
done

echo "==> Trigger label sync (creates/updates standard labels)"
gh workflow run "Sync labels" --repo "$REPO" || true

echo "==> All set. Review the PR if created, then enable required checks on 'main' (already applied)."
