# Deploying to PythonAnywhere

## Static files (images, CSS, JS)

The hero image and other static files work locally but **must be set up** on PythonAnywhere:

### 1. Run collectstatic after every deploy

In a **Bash console** on PythonAnywhere (in your project directory):

```bash
python manage.py collectstatic --noinput
```

This copies everything from `static/` (including `static/video/hero.jpeg`) into `staticfiles/`. Run it whenever you add or change static files.

### 2. Add a Static files mapping in the Web tab

1. Open your PythonAnywhere **Web** tab.
2. Scroll to **Static files**.
3. Add an entry (or fix the existing one):
   - **URL:** `/static/`
   - **Directory:** `/home/YOUR_USERNAME/YOUR_PROJECT_FOLDER/staticfiles`
   - Replace `YOUR_USERNAME` and `YOUR_PROJECT_FOLDER` with your actual path (e.g. `/home/codexware/partyfantasy/staticfiles`).

4. Click **Save**.

After that, `/static/video/hero.jpeg` will be served from `staticfiles/video/hero.jpeg` and the hero image will show on the live site.

### 3. If it still doesn’t show

- Confirm the file exists on the server:  
  `ls -la staticfiles/video/`
- Ensure the filename matches exactly (Linux is case-sensitive):  
  `hero.jpeg` not `hero.JPEG` or `hero.jpg`.
