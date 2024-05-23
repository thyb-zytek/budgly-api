from core.authentication import GoogleAuthorizationUrl, firebase_app, google_flow


async def test_google_flow() -> None:
    flow = google_flow(GoogleAuthorizationUrl(url="https://test.fr/google/sign-in").url)

    assert flow.client_config["project_id"] == "budgly-tracker-app"


async def test_firebase_app() -> None:
    app = firebase_app()

    assert app.project_id == "budgly-tracker-app"
