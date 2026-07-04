User Story: As a user, I want to be able to reset my password using my email address so that I can regain access to my account if I forget my password.

Acceptance Criteria:
1. User enters email and clicks 'Send Reset Link'.
2. If the email exists in our database, send a reset link to that email.
3. If the email does NOT exist, show a generic message to prevent email enumeration attacks.
4. The reset link must expire in exactly 15 minutes.