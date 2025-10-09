# Deployment Guide

This guide explains how to deploy the Global Estuary Type Map to GitHub Pages.

## Quick Deployment (Recommended)

The easiest way to deploy this project is using GitHub Pages directly from your repository.

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings** (top menu)
3. Scroll down to **Pages** in the left sidebar
4. Under **Source**, select:
   - **Branch**: `main` (or your default branch)
   - **Folder**: `/ (root)`
5. Click **Save**

### Step 2: Wait for Deployment

- GitHub will automatically build and deploy your site
- This usually takes 1-2 minutes
- You'll see a green checkmark when it's ready

### Step 3: Access Your Site

Your site will be available at:
```
https://[your-username].github.io/estuary-type-map/
```

For this project specifically:
```
https://nguyentruonganlab.github.io/estuary-type-map/
```

## Custom Domain (Optional)

To use a custom domain like `estuaries.yourdomain.com`:

### Step 1: Add CNAME File

Create a file named `CNAME` in the repository root:
```
estuaries.yourdomain.com
```

### Step 2: Configure DNS

Add these DNS records at your domain provider:

For subdomain (`estuaries.yourdomain.com`):
```
Type: CNAME
Name: estuaries
Value: [your-username].github.io
```

For apex domain (`yourdomain.com`):
```
Type: A
Name: @
Value: 185.199.108.153

Type: A
Name: @
Value: 185.199.109.153

Type: A
Name: @
Value: 185.199.110.153

Type: A
Name: @
Value: 185.199.111.153
```

### Step 3: Enable HTTPS

1. Go to repository Settings → Pages
2. Check **Enforce HTTPS**
3. Wait for SSL certificate to provision (may take up to 24 hours)

## Alternative Deployment Options

### Deploy to Netlify

1. Sign up at [netlify.com](https://www.netlify.com)
2. Click "New site from Git"
3. Connect your GitHub repository
4. Build settings:
   - **Build command**: (leave empty - static site)
   - **Publish directory**: `/`
5. Click "Deploy site"

### Deploy to Vercel

1. Sign up at [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Import from GitHub
4. Framework Preset: Other
5. Click "Deploy"

### Deploy to CloudFlare Pages

1. Sign up at [pages.cloudflare.com](https://pages.cloudflare.com)
2. Connect your GitHub account
3. Select the repository
4. Build settings:
   - **Build command**: (leave empty)
   - **Build output directory**: `/`
5. Click "Save and Deploy"

## Updating the Site

### Automatic Updates

Once deployed, your site automatically updates when you:
1. Push changes to your repository
2. Merge a pull request
3. The GitHub Action runs and updates data

### Manual Data Updates

To manually update estuary data:

1. Edit `scripts/process_estuary_data.py`
2. Run the script locally:
   ```bash
   python3 scripts/process_estuary_data.py
   ```
3. Commit and push the updated `data/estuaries.geojson`
4. Site updates automatically

## Troubleshooting

### Site Not Loading

**Problem**: 404 error or blank page

**Solutions**:
- Wait a few minutes after enabling Pages
- Check that GitHub Pages is enabled in Settings
- Verify the correct branch is selected
- Check that `index.html` is in the root directory

### Map Not Displaying

**Problem**: Map area is blank

**Solutions**:
- Check browser console for errors
- Verify `data/estuaries.geojson` exists and is valid JSON
- Check that Leaflet.js CDN is accessible
- Clear browser cache and reload

### Markers Not Showing

**Problem**: Map loads but no estuary markers appear

**Solutions**:
- Verify GeoJSON file has correct structure
- Check browser console for JavaScript errors
- Ensure coordinates are in [longitude, latitude] order
- Validate GeoJSON at [geojson.io](https://geojson.io)

### Filters Not Working

**Problem**: Checkboxes don't show/hide markers

**Solutions**:
- Check JavaScript console for errors
- Verify `js/map.js` is loaded correctly
- Clear browser cache
- Test in different browser

### Slow Loading

**Problem**: Site takes long time to load

**Solutions**:
- Optimize images if any were added
- Minimize GeoJSON file size
- Consider using marker clustering for large datasets
- Enable caching headers (automatic on GitHub Pages)

## Performance Optimization

### For Large Datasets (1000+ estuaries)

If you add many more estuaries:

1. **Enable Marker Clustering**:
   - Add Leaflet.markercluster library
   - Group nearby markers together
   - Improves performance and readability

2. **Optimize GeoJSON**:
   - Remove unnecessary properties
   - Round coordinates to 4 decimal places
   - Minify JSON file

3. **Lazy Loading**:
   - Load definitions on demand
   - Fetch data in chunks
   - Use pagination for large lists

## Monitoring

### Check Site Status

- GitHub Pages status: [Status page](https://www.githubstatus.com/)
- Your deployment: Repository → Actions tab
- Analytics: Add Google Analytics or Plausible (optional)

### View Build Logs

1. Go to repository → **Actions** tab
2. Click on latest workflow run
3. View detailed logs for each step

## Security

### HTTPS

- Always enabled on GitHub Pages for .github.io domains
- Free SSL certificate included
- Automatic renewal

### Content Security

- GitHub Pages serves static files only
- No server-side code execution
- Safe from most web vulnerabilities
- Keep dependencies (Leaflet.js) updated

## Backup

### Regular Backups

GitHub automatically maintains:
- Full commit history
- All versions of your files
- Can restore any previous state

### Manual Backup

To create a local backup:
```bash
git clone https://github.com/[username]/estuary-type-map.git
cd estuary-type-map
git pull origin main
```

## Advanced Configuration

### Custom 404 Page

Create `404.html` in root directory:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found</title>
</head>
<body>
    <h1>404 - Page Not Found</h1>
    <p><a href="/">Return to Estuary Map</a></p>
</body>
</html>
```

### Redirect Rules

GitHub Pages doesn't support redirects directly. Use JavaScript:
```html
<script>
    window.location.href = '/new-page.html';
</script>
```

### Analytics Integration

Add to `index.html` before `</head>`:

**Google Analytics**:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

**Plausible** (privacy-friendly):
```html
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

## Support

For deployment issues:
- GitHub Pages Documentation: [docs.github.com/pages](https://docs.github.com/pages)
- Open an issue in this repository
- Check GitHub Community: [github.community](https://github.community)

## Checklist

Before deploying, verify:
- [ ] All files are committed and pushed
- [ ] `index.html` is in root directory
- [ ] `data/estuaries.geojson` is valid JSON
- [ ] No broken links in documentation
- [ ] Site tested locally
- [ ] README is up to date
- [ ] GitHub Pages is enabled in Settings

After deploying, verify:
- [ ] Site loads at GitHub Pages URL
- [ ] Map displays correctly
- [ ] Markers appear in correct locations
- [ ] Filters work properly
- [ ] Popups show correct information
- [ ] Mobile view is responsive
- [ ] No console errors
- [ ] HTTPS is enabled

---

Your Global Estuary Type Map is now live! 🌊🗺️
