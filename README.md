# Tribulation of Myriad Realms - Web Novel Reader

A beautiful, auto-updating web novel reader for "Tribulation of Myriad Realms" (万界劫), inspired by popular platforms like Webnovel and Wuxiaworld.

## Features

- 📖 Clean, modern reading interface
- 🎨 Beautiful design inspired by Webnovel/Wuxiaworld
- 📱 Fully responsive (works on mobile, tablet, and desktop)
- ⌨️ Keyboard navigation (← → arrow keys)
- 💾 Remembers your reading position
- 🔄 Auto-updates from GitHub when you push new chapters
- 🚀 Fast loading and smooth navigation

## Setup Instructions

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it whatever you'd like (e.g., `tribulation-webnovel`)
3. Make it public (required for free GitHub Pages)

### 2. Upload Your Files

Upload these files to your GitHub repository:
- `index.html`
- `styles.css`
- `app.js`
- `.github/workflows/deploy.yml`
- `en_chapters/` folder with your translated chapters

You can do this via:
- **GitHub web interface**: Click "Add file" → "Upload files"
- **Git command line** (from this directory):
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  git branch -M main
  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
  git push -u origin main
  ```

### 3. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings" → "Pages"
3. Under "Source", select "GitHub Actions"
4. Save

### 4. Wait for Deployment

- The GitHub Action will automatically run when you push
- It will build and deploy your site
- Check the "Actions" tab to see the deployment progress
- Once complete (green checkmark), your site will be live at:
  `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`

## Adding New Chapters

Simply add new `.txt` files to the `en_chapters/` folder following the naming pattern:
- `ch_664.txt`
- `ch_665.txt`
- etc.

Then push to GitHub:
```bash
git add en_chapters/
git commit -m "Added chapters 670-675"
git push
```

The site will automatically rebuild and update within a few minutes!

## File Structure

```
tribulation-of-myriad-realms/
├── index.html              # Main HTML page
├── styles.css              # Styling
├── app.js                  # JavaScript functionality
├── .github/
│   └── workflows/
│       └── deploy.yml      # Auto-deployment workflow
├── en_chapters/            # Your translated chapters
│   ├── ch_664.txt
│   ├── ch_665.txt
│   └── ...
└── README.md              # This file
```

## Local Testing

To test locally before pushing to GitHub:

1. Open a terminal in this directory
2. Start a local web server:
   ```bash
   # Python 3
   python -m http.server 8000
   
   # Or Python 2
   python -m SimpleHTTPServer 8000
   ```
3. Open your browser to `http://localhost:8000`

## Customization

### Change Colors
Edit `styles.css` and modify the CSS variables:
```css
:root {
    --primary-color: #f26522;      /* Orange accent */
    --secondary-color: #1a1a2e;    /* Dark blue */
    /* ... */
}
```

### Change Novel Title
Edit `index.html` and update:
- `<title>` tag
- `.nav-brand` text
- `.novel-title` text

### Add a Cover Image
Replace the `.cover-placeholder` div in `index.html` with:
```html
<img src="cover.jpg" alt="Novel Cover" style="width: 200px; border-radius: 8px;">
```

## Troubleshooting

**Chapters not loading?**
- Make sure chapter files are named correctly: `ch_NUMBER.txt`
- Check that files are in the `en_chapters/` folder
- Verify the GitHub Action completed successfully

**Site not updating?**
- Go to the "Actions" tab in your GitHub repo
- Check if the latest workflow ran successfully
- If it failed, click on it to see the error logs

**404 Error?**
- Make sure GitHub Pages is enabled
- Wait a few minutes after the first deployment
- Check the exact URL in Settings → Pages

## License

This is a personal project for reading translated web novels.

## Credits

Translation by AI (Google Gemini)
Website inspired by Webnovel and Wuxiaworld
