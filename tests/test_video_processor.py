"""
VideoProcessor 單元測試

聚焦於 combine_ts_to_mp4 的 ffmpeg 失敗處理：
- 找不到 ffmpeg 時回傳 False（而非於下載完成後崩潰）
- ffmpeg 回傳非 0 時回傳 False
- 正常合併回傳 True
所有測試皆離線，不實際呼叫 ffmpeg。
"""

from unittest.mock import MagicMock, patch

from rich.console import Console

from package.processors.VideoProcessor import VideoProcessor


def make_processor(tmp_path):
    return VideoProcessor(
        network_manager=MagicMock(),
        base_path=str(tmp_path),
        console=Console(),
    )


def _write_media_txt(tmp_path):
    (tmp_path / "media.txt").write_text("file '0.ts'\n", encoding="utf-8")


@patch("package.processors.VideoProcessor.shutil.which", return_value=None)
def test_combine_returns_false_when_ffmpeg_missing(_which, tmp_path):
    """找不到 ffmpeg 時應回傳 False，不啟動子程序"""
    processor = make_processor(tmp_path)
    _write_media_txt(tmp_path)

    with patch("package.processors.VideoProcessor.subprocess.Popen") as popen:
        result = processor.combine_ts_to_mp4(save_path=str(tmp_path))

    assert result is False
    popen.assert_not_called()


@patch("package.processors.VideoProcessor.shutil.which", return_value="/usr/bin/ffmpeg")
def test_combine_returns_false_on_nonzero_returncode(_which, tmp_path):
    """ffmpeg 回傳非 0 時應回傳 False"""
    processor = make_processor(tmp_path)
    _write_media_txt(tmp_path)

    fake_pop = MagicMock()
    fake_pop.poll.return_value = 1  # 迴圈不進入
    fake_pop.returncode = 1

    with patch(
        "package.processors.VideoProcessor.subprocess.Popen", return_value=fake_pop
    ):
        result = processor.combine_ts_to_mp4(save_path=str(tmp_path))

    assert result is False


@patch("package.processors.VideoProcessor.shutil.which", return_value="/usr/bin/ffmpeg")
def test_combine_returns_true_on_success(_which, tmp_path):
    """ffmpeg 回傳 0 時應回傳 True"""
    processor = make_processor(tmp_path)
    _write_media_txt(tmp_path)

    fake_pop = MagicMock()
    fake_pop.poll.return_value = 0
    fake_pop.returncode = 0

    with patch(
        "package.processors.VideoProcessor.subprocess.Popen", return_value=fake_pop
    ):
        result = processor.combine_ts_to_mp4(save_path=str(tmp_path))

    assert result is True


@patch("package.processors.VideoProcessor.shutil.which", return_value="/usr/bin/ffmpeg")
def test_combine_returns_false_when_popen_raises(_which, tmp_path):
    """Popen 拋出 OSError（如 ffmpeg 突然不可執行）時應回傳 False 而非往外拋"""
    processor = make_processor(tmp_path)
    _write_media_txt(tmp_path)

    with patch(
        "package.processors.VideoProcessor.subprocess.Popen",
        side_effect=OSError("cannot exec"),
    ):
        result = processor.combine_ts_to_mp4(save_path=str(tmp_path))

    assert result is False
