"""
Verify CSRF protection is implemented.

EECS 485 Project 2

Sydney Shanahan <shanahsy@umich.edu>
Garv Shah <garvshah@umich.edu>
"""

import re
import bs4

# We need to import test fixtures in specific test files because the fixture
# imports student code (like the app tests).  If the student isn't finished
# with their code, then earlier tests (like database tests) won't even run.
# pylint: disable-next=unused-import
from app_fixtures import setup_teardown_client

import insta485


def test_csrf_comment(client):
    """Verify CSRF protection on /comments/ URL."""

    # Configure Flask app to ensure CSRF checking is enabled
    insta485.app.config["WTF_CSRF_ENABLED"] = True

    # Load the login page to get the CSRF token.
    response = client.get("/accounts/login/")
    assert response.status_code == 200

    # Parse CSRF token from HTML form on the login page
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]

    # Login in with CSRF token
    response = client.post(
        "/accounts/",
        data={
            "username": "awdeorio",
            "password": "chickens",
            "operation": "login",
            "csrf_token": csrf_token,
        },
    )
    assert response.status_code == 302

    # Submit a comment with no CSRF token should fail
    response = client.post(
        "comments/",
        data={
            "operation": "create",
            "postid": 1,
            "text": "This is a malicious comment",
        },
    )
    assert response.status_code == 400

    # Load and parse /posts/1/ page
    response = client.get("/posts/1/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify expected content is in text on generated HTML page
    assert text.count("awdeorio") == 3
    assert "This is a malicious comment" not in text

    # Submit a comment with hardcoded CSRF token should fail
    response = client.post(
        "comments/",
        data={
            "operation": "create",
            "postid": 1,
            "text": "This is a malicious comment",
            "csrf_token": "ImI2ODY0Y2NjYTg5MzcyYTMwMzYyNzAyYzA3YzkwMjAwN2Y3"
            "NDcxMzQi.aLn8bQ.KJkrW6oQeILwmvl71qDA4YcXNx4",
        },
    )
    assert response.status_code == 400

    # Load and parse /posts/1/ page
    response = client.get("/posts/1/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify expected content is in text on generated HTML page
    assert text.count("awdeorio") == 3
    assert "This is a malicious comment" not in text

    # Load the login page to get the CSRF token
    response = client.get("/posts/1/")
    assert response.status_code == 200

    # Parse CSRF token from form
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    # Find the form for creating a new comment
    comment_form = soup.find("form", {"action": "/comments/?target=/posts/1/"})

    # Extract the CSRF token
    csrf_token = comment_form.find("input", {"name": "csrf_token"})["value"]

    # Submit a comment with the valid CSRF token
    response = client.post(
        "comments/",
        data={
            "operation": "create",
            "postid": 1,
            "text": "This is not a malicious comment",
            "csrf_token": csrf_token,
        },
    )
    assert response.status_code == 302

    # Load and parse /posts/1/ page
    response = client.get("/posts/1/")
    assert response.status_code == 200
    soup = bs4.BeautifulSoup(response.data, "html.parser")
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)

    # Verify expected content is in text on generated HTML page
    assert text.count("awdeorio") == 4
    assert "This is not a malicious comment" in text
