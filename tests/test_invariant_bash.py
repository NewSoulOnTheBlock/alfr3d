import pytest
from agent.tools.bash.bash import Bash


@pytest.mark.parametrize("command", [
    "cat ~/.alfr3d/.env",
    "cat .alfr3d/.env",
    "less ~/.alfr3d/.env",
    "cat /home/user/.alfr3d/.env",
])
def test_credential_file_access_is_blocked(command):
    result = Bash().execute({"command": command})
    assert result.status == "error", f"Expected blocked result for: {command}"
    assert "Access denied" in str(result.result)


@pytest.mark.parametrize("command", [
    "ls ~/.alfr3d/skills",
    "ls ~/.alfr3d/",
    "echo hello",
])
def test_legitimate_alfr3d_directory_access_is_not_blocked(command):
    result = Bash().execute({"command": command})
    assert "Access denied" not in str(result.result)
