## Branching Strategy

We follow a **trunk-based development** model with a single main branch and short-lived feature branches.

### Branch Types

1. **main** - The primary development branch
   - Always deployable
   - All features merge here
   - Protected with required reviews

2. **feature/*** - Short-lived feature branches
   - Created from main
   - Merged back to main via Pull Request
   - Deleted after merge

3. **hotfix/*** - Emergency fixes
   - Created from main
   - Fast-tracked review process
   - Merged directly to main

### Workflow

1. **Create a Feature Branch**

   ```bash
   # Ensure you're on main and up to date
   git checkout main
   git pull upstream main
   
   # Create and checkout a new feature branch
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**

   - Keep commits small and focused
   - Write clear commit messages
   - Test your changes thoroughly

3. **Push and Create Pull Request**

   ```bash
   # Push your branch to your fork
   git push origin feature/your-feature-name
   ```
   
   Then create a Pull Request on GitHub targeting the `main` branch.
