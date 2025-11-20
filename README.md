## 🐛 Bug Report: Automation Blockers

While building this agent, I identified critical issues preventing standard automation flows:

1.  404 on Direct Access: Navigating to `https://events.webmobi.com/login` results in a 404 error, breaking standard deep-linking strategies.
2.  Dynamic DOM Elements: The Login button on the homepage is inconsistent or obscured by cookie banners, causing `ElementNotFound` errors.
3.  Recommendation: The application requires stable `id` attributes (e.g., `id="login-btn"`) to be automation-friendly.
