# Alternative: GitHub Pages with gh-pages branch

If you prefer the traditional approach with a separate `gh-pages` branch, here's the workflow modification:

```yaml
name: Deploy MkDocs to GitHub Pages (gh-pages branch)

on:
  push:
    branches: [ main ]
    paths: 
      - 'docs/**'
      - 'mkdocs.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install mkdocs mkdocs-material mkdocs-material-extensions pymdown-extensions mkdocs-git-revision-date-localized-plugin mkdocs-minify-plugin

      - name: Deploy to gh-pages
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          mkdocs gh-deploy --force
```

## Pros and Cons

### ✅ gh-pages branch approach:
- Traditional and familiar
- MkDocs has built-in support (`mkdocs gh-deploy`)
- Some developers prefer separate branches

### ❌ gh-pages branch drawbacks:
- Creates a separate branch with build artifacts
- Less secure (uses personal tokens)
- Clutters repository history
- Older approach

## Recommendation

**Keep your current setup!** It's following modern GitHub Pages best practices and is more secure and cleaner than the gh-pages branch approach.
