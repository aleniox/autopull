import os
import time
import subprocess
import logging
import sys

# Thiết lập logging với encoding='utf-8'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('git_pull.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class GitAutoPuller:
    def __init__(self, repo_path, branch='main', check_interval=300, main_program=None):
        """
        Khởi tạo GitAutoPuller
        
        :param repo_path: Đường dẫn đến repository local
        :param branch: Nhánh cần theo dõi (mặc định là 'main')
        :param check_interval: Thời gian giữa các lần kiểm tra (tính bằng giây)
        :param main_program: Đường dẫn đến file chương trình chính cần restart
        """
        self.repo_path = repo_path
        self.branch = branch
        self.check_interval = check_interval
        self.main_program = main_program
        self.last_commit = self.get_current_commit()
        self.process = None

    def get_current_commit(self):
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Lỗi khi lấy commit hiện tại: {str(e)}")
            return None

    def fetch_updates(self):
        try:
            subprocess.run(
                ['git', 'fetch', 'origin', self.branch],
                cwd=self.repo_path,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Lỗi khi fetch updates: {str(e)}")
            return False

    def has_updates(self):
        try:
            result = subprocess.run(
                ['git', 'rev-parse', f'origin/{self.branch}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            remote_commit = result.stdout.strip()
            return remote_commit != self.last_commit
        except subprocess.CalledProcessError as e:
            logging.error(f"Lỗi khi kiểm tra updates: {str(e)}")
            return False

    def pull_changes(self):
        try:
            subprocess.run(
                ['git', 'pull', 'origin', self.branch],
                cwd=self.repo_path,
                check=True
            )
            self.last_commit = self.get_current_commit()
            logging.info("Pull thành công các thay đổi mới")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Lỗi khi pull changes: {str(e)}")
            return False

    def start_main_program(self):
        """Khởi động chương trình chính"""
        if not self.main_program:
            return
        
        try:
            # Tắt process cũ nếu đang chạy
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait()
                logging.info("Đã tắt chương trình cũ")

            # Khởi động process mới
            self.process = subprocess.Popen(
                [sys.executable, self.main_program],
                cwd=self.repo_path
            )
            logging.info(f"Đã khởi động lại chương trình: {self.main_program}")
        except Exception as e:
            logging.error(f"Lỗi khi khởi động lại chương trình: {str(e)}")

    def start_monitoring(self):
        """Bắt đầu theo dõi repository"""
        logging.info(f"Bắt đầu theo dõi repository tại {self.repo_path}")
        logging.info(f"Branch: {self.branch}")
        logging.info(f"Kiểm tra cập nhật mỗi {self.check_interval} giây")
        
        # Khởi động chương trình chính lần đầu
        self.start_main_program()

        while True:
            try:
                if self.fetch_updates() and self.has_updates():
                    logging.info("Phát hiện thay đổi mới!")
                    if self.pull_changes():
                        self.start_main_program()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                logging.info("Dừng theo dõi repository")
                if self.process and self.process.poll() is None:
                    self.process.terminate()
                break
            except Exception as e:
                logging.error(f"Lỗi không mong muốn: {str(e)}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    # Đảm bảo Python sử dụng UTF-8 cho stdout
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Cấu hình
    REPO_PATH = "D:/NB"
    BRANCH = "main"
    CHECK_INTERVAL = 30  # 5 phút
    MAIN_PROGRAM = "main.py"  # Tên file chương trình chính cần restart

    auto_puller = GitAutoPuller(
        repo_path=REPO_PATH,
        branch=BRANCH,
        check_interval=CHECK_INTERVAL,
        main_program=MAIN_PROGRAM
    )
    auto_puller.start_monitoring()