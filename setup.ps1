Param(
  [Parameter(Mandatory=$true)][string]$Repo,
  [string]$ReviewerLogin
)

function Require-GH {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is required. Install: https://cli.github.com/"
    exit 1
  }
}
Require-GH

Write-Host "==> Checking repo access for $Repo"
gh repo view $Repo | Out-Null

Write-Host "==> Setting repo options"
gh repo edit $Repo --default-branch main --delete-branch-on-merge --allow-update-branch --enable-automated-security-fixes --enable-vulnerability-alerts --add-topic repo-pilot --add-topic templates | Out-Null

# Copy .github files by cloning into a temp folder
$tmp = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath()) -Name ("repo-pilot-" + [System.Guid]::NewGuid().ToString()) -Force
git clone "https://github.com/$Repo.git" $tmp.FullName | Out-Null
robocopy ".github" (Join-Path $tmp.FullName ".github") /E | Out-Null
Copy-Item "SECURITY.md" (Join-Path $tmp.FullName "SECURITY.md") -Force

Push-Location $tmp.FullName
git add .
$hasChanges = $false
try { git diff --cached --quiet } catch { $hasChanges = $true }
if ($hasChanges) {
  git config user.name "repo-pilot"
  git config user.email "repo-pilot@example.com"
  git commit -m "chore(repo-pilot): add workflows, templates, labels, dependabot" | Out-Null
  git push origin HEAD:repo-pilot/bootstrap | Out-Null
  gh pr create --repo $Repo --base main --head repo-pilot/bootstrap --title "chore(repo-pilot): bootstrap workflows & templates" --body "Adds CI, labeler, templates, Dependabot, and protections." | Out-Null
} else {
  Write-Host "No .github changes to commit."
}
Pop-Location

Write-Host "==> Creating/Updating branch protection for 'main'"
gh api -X PUT "repos/$Repo/branches/main/protection" -H "Accept: application/vnd.github+json" `
  -F required_status_checks.strict=true `
  -F required_status_checks.contexts[]="lint" `
  -F required_status_checks.contexts[]="semantic-pr" `
  -F enforce_admins=true `
  -F required_pull_request_reviews.required_approving_review_count=1 `
  -F required_pull_request_reviews.dismiss_stale_reviews=true `
  -F required_pull_request_reviews.require_code_owner_reviews=false `
  -F restrictions= `
  -F allow_deletions=false `
  -F allow_force_pushes=false `
  -F required_linear_history=true `
  -F required_conversation_resolution=true | Out-Null

Write-Host "==> Creating environments (staging, production)"
if ($ReviewerLogin) {
  $rid = gh api "users/$ReviewerLogin" --jq ".id"
  foreach ($env in @("staging","production")) {
    gh api -X PUT "repos/$Repo/environments/$env" -H "Accept: application/vnd.github+json" `
      -f wait_timer=0 `
      -f deployment_branch_policy.custom_branch_policies=false `
      -f "reviewers[0][type]=User" `
      -f "reviewers[0][id]=$rid" | Out-Null
  }
} else {
  foreach ($env in @("staging","production")) {
    gh api -X PUT "repos/$Repo/environments/$env" -H "Accept: application/vnd.github+json" `
      -f wait_timer=0 `
      -f deployment_branch_policy.custom_branch_policies=false | Out-Null
  }
}

Write-Host "==> Trigger label sync workflow"
gh workflow run "Sync labels" --repo $Repo | Out-Null

Write-Host "==> Done."
