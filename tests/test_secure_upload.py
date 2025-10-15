from pathlib import Path

from app.security.upload_secure import secure_save, sniff_image_type


def test_sniff_image_type_ok_png():
    assert sniff_image_type(b"\x89PNG\r\n\x1a\n123") == "image/png"


def test_secure_save_too_big(tmp_path: Path):
    data = b"\x89PNG\r\n\x1a\n" + b"0" * 5_000_001
    try:
        secure_save(tmp_path, data)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert str(e) == "too_big"


def test_secure_save_bad_type(tmp_path: Path):
    try:
        secure_save(tmp_path, b"not an image")
        assert False
    except ValueError as e:
        assert str(e) == "bad_type"


def test_secure_save_ok_jpeg(tmp_path: Path):
    jpeg = b"\xff\xd8" + b"0" * 10 + b"\xff\xd9"
    p = secure_save(tmp_path, jpeg)
    assert p.endswith(".jpg")
