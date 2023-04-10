

class FaceBookSelector:
    # base
    input_login: str = 'input#email'
    input_password: str = 'input#pass'
    app_id: str = 'span[value]'
    check_login: str = 'input[type="search"]'
    second_check_login: str = 'i[data-visualcomletion]'
    # check_login: str = 'a[aria-label="Home"]'
    input_accounts: str = 'form[data-testid="advanced_settings_page"]'
    save_changes_button: str = 'button[name="save_changes"]'
    check_accs: str = 'span[draggable="false"]'
    element_to_delete: str = 'div[role="button"]'
    # confirm acc by email... 
    checkpoint_form: str = 'form[action="/checkpoint/?next"]'
    checkpoint_continue: str = 'button#checkpointSubmitButton'
    verification_method: str = 'input[name="verification_method"]'
    continuing_btn: str = 'button[type="button"]' # ('Upload ID', 'Next', 'Send')  are the text into tag
    enter_email: str = 'input[placeholder="Email Address"]'
    confirm_email: str = 'input[placeholder="Confirm Email Address"]'
    verify_code: str = 'input[placeholder="Verification code"]'
    set_number: str = 'input[name="captcha_response"]'
    # confirm 2fa
    login_code: str = 'input#approvals_code'
    submin_login: str = 'button[name="submit[This was me]"]'
    accept_cookies: str = 'button[data-cookiebanner="accept_button"]'
