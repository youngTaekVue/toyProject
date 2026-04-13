import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

# 로그 저장 경로 설정: accountbook/logs 폴더
# 현재 파일(Logger.py) 위치가 accountbook/utils이므로, 상위 폴더인 accountbook 아래에 logs 생성
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 로그 폴더가 없으면 생성
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app_activity.log")

class AppLogger:
    _instance = None
    logs = []  # 메모리에 로그 저장 (UI 리스트업용)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        self.logger = logging.getLogger("AccountBook")
        self.logger.setLevel(logging.INFO)

        # TimedRotatingFileHandler 설정: 매일 자정(midnight)에 로그 파일 교체
        fh = TimedRotatingFileHandler(
            LOG_FILE, 
            when="midnight", 
            interval=1, 
            backupCount=30, 
            encoding='utf-8'
        )
        # 백업 파일명 형식 설정 (app_activity.log.YYYY-MM-DD)
        fh.suffix = "%Y-%m-%d"
        
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # 앱 시작 시 최근 로그 로드 (현재 로그 + 백업 로그 일부)
        self._load_all_recent_logs()

    def _load_all_recent_logs(self):
        """현재 로그 파일과 백업된 이전 날짜 로그 파일들을 모두 읽어 메모리에 로드"""
        self.logs = []
        log_base_name = os.path.basename(LOG_FILE)
        
        # 로그 폴더 내의 모든 파일 목록 가져오기
        if not os.path.exists(LOG_DIR):
            return
            
        log_files = []
        for f in os.listdir(LOG_DIR):
            # 현재 로그 파일(app_activity.log) 또는 백업 파일(app_activity.log.YYYY-MM-DD)
            if f == log_base_name or f.startswith(log_base_name + "."):
                log_files.append(os.path.join(LOG_DIR, f))
        
        # 파일명 순서대로 정렬 (날짜순)
        log_files.sort()

        for file_path in log_files:
            self._parse_log_file(file_path)

    def _parse_log_file(self, file_path):
        """개별 로그 파일을 파싱하여 self.logs에 추가"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(' | ')
                    if len(parts) >= 4:
                        time_str = parts[0].split(',')[0]
                        source_msg = parts[3]
                        source = parts[2]
                        message = source_msg
                        
                        if source_msg.startswith('[') and ']' in source_msg:
                            message = source_msg.split(']', 1)[1].strip()

                        self.logs.append({
                            "time": time_str,
                            "level": parts[1],
                            "source": source,
                            "message": message
                        })
        except Exception as e:
            print(f"Error parsing log file {file_path}: {e}")

    def log(self, level, source, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "time": timestamp,
            "level": level,
            "source": source,
            "message": message
        }
        self.logs.append(log_entry)

        if level == "INFO": self.logger.info(f"[{source}] {message}")
        elif level == "WARNING": self.logger.warning(f"[{source}] {message}")
        elif level == "ERROR": self.logger.error(f"[{source}] {message}")

# 싱글톤 인스턴스
logger = AppLogger()
