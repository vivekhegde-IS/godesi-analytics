"""Make a NEW RSA key pair for GitHub Actions (separate from the key on your laptop).

Why a separate key: if GitHub's copy ever leaks, you remove only that key in Snowflake and your laptop keeps
working. Snowflake lets one user have two public keys (RSA_PUBLIC_KEY and RSA_PUBLIC_KEY_2) for exactly this.

Run with the project venv (it has the cryptography package):
    .venv\\Scripts\\python.exe scripts\\make_key_pair.py
It writes two files OUTSIDE the repo, in ~/.ssh/snowflake/:
    github_actions_key.p8   private key -> paste its full text into the GitHub secret SNOWFLAKE_PRIVATE_KEY
    github_actions_key.pub  public key  -> goes into Snowflake (the script prints the ALTER USER statement)
The private key is never printed. Nothing is written to the repo.
"""
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

OUT = Path.home() / ".ssh" / "snowflake"
PRIVATE, PUBLIC = OUT / "github_actions_key.p8", OUT / "github_actions_key.pub"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if PRIVATE.exists():
        raise SystemExit(f"{PRIVATE} already exists: delete it first if you really want a new key.")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    PRIVATE.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                          serialization.NoEncryption()))
    pub = key.public_key().public_bytes(serialization.Encoding.PEM,
                                        serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    PUBLIC.write_text(pub)
    body = "".join(line for line in pub.splitlines() if "-----" not in line)
    print(f"Private key: {PRIVATE}  (keep it secret; paste its text into the GitHub secret)")
    print(f"Public key:  {PUBLIC}")
    print("\nRun this in Snowsight as SECURITYADMIN (the public key is not secret):\n")
    print(f"alter user DBT_USER set rsa_public_key_2 = '{body}';")


if __name__ == "__main__":
    main()
