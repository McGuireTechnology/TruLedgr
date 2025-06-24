# Git and GitHub Guide

## What is Git?

Git is a distributed version control system that helps developers track changes in their codebase, collaborate with others, and manage project history. It allows you to record snapshots of your project over time, revert to previous versions, and work on different features or fixes in parallel using branches. Git is widely used in both open-source and private projects for its speed, flexibility, and powerful collaboration features.

## What is GitHub?

GitHub is a web-based platform for hosting and collaborating on Git repositories. It provides tools for version control, code review, issue tracking, and project management, making it easier for individuals and teams to work together on software projects. GitHub also enables open-source collaboration, allowing developers to contribute to public repositories, fork projects, and submit pull requests. Its integration with Git streamlines workflows and helps maintain a transparent and organized development process.

## Basic Git Commands

- `git init` – Initialize a new Git repository
- `git clone <repo>` – Clone a repository
- `git status` – Show the working tree status
- `git add <file>` – Stage changes
- `git commit -m "message"` – Commit staged changes
- `git log` – View commit history
- `git diff` – Show changes between commits, commit and working tree, etc.

## Branching and Merging

- `git branch` – List, create, or delete branches
- `git checkout <branch>` – Switch branches
- `git merge <branch>` – Merge a branch into the current branch
- Resolving merge conflicts: Edit conflicted files, then `git add` and `git commit`

## Working with Remotes

- `git remote add <name> <url>` – Add a remote repository
- `git fetch` – Download objects and refs from another repository
- `git pull` – Fetch and merge changes from the remote
- `git push` – Push local changes to the remote

## Pull Requests and Code Review

- Create a pull request on GitHub to propose changes
- Review code, discuss, and request changes before merging

## Undoing Changes

- `git checkout -- <file>` – Discard changes in working directory
- `git reset <file>` – Unstage a file
- `git revert <commit>` – Revert a commit by creating a new one

## Stashing Changes

- `git stash` – Save changes for later
- `git stash pop` – Re-apply stashed changes

## Tagging Releases

- `git tag <tagname>` – Create a tag
- `git push --tags` – Push tags to remote

## Best Practices

- Write clear, concise commit messages
- Use descriptive branch names
- Keep branches up to date with main
- Review code before merging

## Understanding .gitignore Files

A `.gitignore` file tells Git which files or directories to ignore in your project. This is important for keeping your repository clean by preventing unnecessary files—such as build artifacts, logs, or sensitive data—from being tracked and pushed to your remote repository.

### Modularizing .gitignore

In this project, we modularize our `.gitignore` setup by placing `.gitignore` files in relevant subdirectories. This allows each module or component to specify its own ignore rules, making the configuration more maintainable and context-specific.

### Sourcing from GitHub's gitignore Repository

The core ignore patterns are sourced from the official [GitHub gitignore repository](https://github.com/github/gitignore). This ensures we follow best practices for ignoring files specific to our languages and tools, and makes it easy to update our ignore rules as standards evolve.

By combining modular `.gitignore` files with community-sourced patterns, we keep our repository organized and up to date with industry standards.

## References and Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)
- [GitHub gitignore Templates](https://github.com/github/gitignore)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
