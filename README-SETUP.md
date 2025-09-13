# repo-pilot starter

**What you get**
- CI workflow with Super-Linter, PR title check (semantic), auto-labeler
- Issue & PR templates, CODEOWNERS, SECURITY policy
- Label catalog + sync workflow
- Dependabot for GitHub Actions, npm, pip
- Scripts to apply GitHub settings: branch protection, environments, topics, security alerts

## How to use

1. Install **GitHub CLI** and login:  
   ```bash
   gh auth login
   ```

2. Add these files to your repository root (keep the `.github` folder intact).

3. Apply settings (Bash):
   ```bash
   ./scripts/setup.sh OWNER/REPO [REVIEWER_LOGIN]
   ```

   Or PowerShell:
   ```powershell
   ./scripts/setup.ps1 -Repo OWNER/REPO -ReviewerLogin REVIEWER_LOGIN
   ```

   - `OWNER/REPO` 예: `parkcheolhong/repo-pilot`
   - `REVIEWER_LOGIN` 은 환경 승인자가 될 깃허브 아이디(선택).

4. Open the created PR **"chore(repo-pilot): bootstrap workflows & templates"** and merge it.
5. Try opening a test PR: labeler + semantic check + linter가 자동으로 동작합니다.

> Branch protection에서 필요한 체크 이름은 **`lint`**, **`semantic-pr`** 로 미리 설정되어 있습니다.

## Notes
- Scripts use `gh api` against:
  - **Branch protection** (PUT `/repos/{owner}/{repo}/branches/main/protection`)
  - **Environments** (PUT `/repos/{owner}/{repo}/environments/{name}`)
- You can add more required checks later from the repository settings if you add language-specific tests.
