# Elite Academy - School Website

A professional, fully-responsive school website built with HTML, CSS, and JavaScript.

## 📋 Project Structure

```
school-website/
├── index.html          # Homepage
├── about.html          # About the school
├── courses.html        # Courses and programs
├── contact.html        # Contact information & form
├── style.css           # All styling
├── script.js           # Interactive features
└── README.md           # This file
```

## 🌐 Pages

### 1. **Home (index.html)**
- Hero section with call-to-action button
- Feature cards highlighting school strengths
- Statistics section showing school achievements
- Testimonials from students

### 2. **About (about.html)**
- School history and story
- Mission and vision statements
- Core values
- Leadership team profiles
- School achievements

### 3. **Courses (courses.html)**
- Elementary, Middle, and High school programs
- Special programs (Athletics, Arts, Technology, etc.)
- Extracurricular activities

### 4. **Contact (contact.html)**
- Contact information and hours
- Contact form with validation
- Admissions information
- Application process details
- Map section (placeholder)

## ✨ Features

- **Responsive Design**: Fully responsive on mobile, tablet, and desktop
- **Modern UI**: Clean, professional design with smooth animations
- **Interactive Elements**:
  - Navigation highlighting
  - Scroll animations
  - Counter animations for statistics
  - Form validation
  - Success/error messages
  - Ripple effects on buttons
- **Accessibility**: Semantic HTML, proper contrast ratios
- **Performance**: Optimized CSS and minimal JavaScript

## 🚀 Using Live Server

To view the website with hot-reload:

1. **Open the folder in VS Code**
   ```bash
   code /workspaces/SWAT-COMPLETE-WEATHER-DATA-DOWNLOADER/school-website
   ```

2. **Right-click on index.html** and select **"Open with Live Server"**

3. Your browser will open at `http://localhost:5500`

4. **Auto-reload**: Any changes you make to HTML, CSS, or JavaScript will automatically refresh in the browser

## 📝 Customization

### Colors
Edit the CSS variables in `style.css`:
```css
:root {
    --primary-color: #2c3e50;      /* Main color */
    --secondary-color: #3498db;    /* Accent color */
    --accent-color: #e74c3c;       /* Highlight color */
}
```

### Content
- Edit school name, address, phone in HTML files
- Update teacher names and information in `about.html`
- Modify course descriptions in `courses.html`
- Update contact information in `contact.html`

### Contact Form
The form currently saves submissions to browser's local storage. To make it functional:
- Replace the form submission handler with actual backend API
- Use services like FormSubmit, Netlify Forms, or your own backend

## 🎨 Design Features

- **Color Scheme**:
  - Primary: Dark Blue (#2c3e50)
  - Secondary: Bright Blue (#3498db)
  - Accent: Red (#e74c3c)
  - Backgrounds: Light Gray (#ecf0f1)

- **Typography**:
  - Font Family: Segoe UI, Tahoma, Geneva, Verdana
  - Clear hierarchy with varied font sizes
  - Good line-height for readability

- **Animations**:
  - Smooth transitions
  - Scroll-triggered animations
  - Button hover effects
  - Counter animations for statistics

## 📱 Responsive Breakpoints

- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: Below 768px

## 🔧 JavaScript Features

1. **Navigation**: Active link highlighting based on current page
2. **Form Validation**: Email validation, required field checks
3. **Animations**: 
   - Fade-in on scroll (Intersection Observer)
   - Counter animations for stats
   - Ripple effects on buttons
4. **Local Storage**: Saves contact form submissions
5. **Analytics**: Tracks page views

## 📄 File Details

### index.html
- Largest file with hero section
- Feature cards, statistics, testimonials
- Links to other pages

### about.html
- School information and history
- Leadership team section
- Achievements list

### courses.html
- Course card system
- Special programs grid
- Extracurricular activities

### contact.html
- Contact information cards
- Working contact form
- Admission information
- Application process

### style.css
- 830+ lines of CSS
- Mobile-first responsive design
- CSS Grid and Flexbox layouts
- Smooth transitions and animations

### script.js
- Navigation highlighting
- Form validation and submission
- Scroll animations
- Counter animations
- Local storage integration

## 🎯 Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## 💡 Tips

1. Use developer tools (F12) to test responsiveness
2. Check console for any JavaScript errors
3. Test all form fields with validation
4. Verify all navigation links work correctly
5. Test animations by scrolling through the page

## 📧 Contact Form

Currently uses local browser storage. To integrate with email:

### Option 1: FormSubmit (No backend needed)
```html
<form action="https://formsubmit.co/YOUR_EMAIL@example.com" method="POST">
    <!-- form fields -->
</form>
```

### Option 2: Netlify Forms
Deploy on Netlify and add `netlify` attribute to form

### Option 3: Backend API
Connect to your own server/API endpoint

## 🔒 Security Notes

- Form currently doesn't send emails to protect privacy
- Email validation is client-side only
- For production, add server-side validation
- Sanitize all user inputs on backend

## 📈 Future Enhancements

- [ ] Add image carousel/gallery
- [ ] Integrate with email service (SendGrid, Mailgun)
- [ ] Add blog/news section
- [ ] Student portal login
- [ ] Event calendar
- [ ] Staff directory with photos
- [ ] Online enrollment system
- [ ] Parent-teacher communication portal
- [ ] Student achievements showcase
- [ ] Video testimonials

## 📝 License

This project is open source and available for educational use.

---

**Made with ❤️ for Elite Academy**
