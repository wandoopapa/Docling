# Docling 변환 프로그램 매뉴얼 (최종 정리본)

- 문서 버전: **v43.1 (2026-02-15)**
- 기준 문서: `docs/Docling 변환 프로그램 메뉴얼_2602150743.md`
- 목적: 최종 운영 구조를 유지하면서 설치 절차/실행 명령어를 즉시 실행 가능한 형태로 제공

---

## 1) 시스템 개요

본 시스템은 기구 설계 PDF를 LLM 학습용 텍스트 데이터셋으로 변환하는 ETL 도구입니다.

핵심 목표:
1. 재현 가능한 설치
2. 장애 원인 추적 가능한 로그
3. 재시작/복구 정책의 명확한 제어
4. 문서와 실제 동작의 일치

---

## 2) 최종 운영 구조

```text
Docling/
├─ README.md
├─ CHANGELOG.md
├─ requirements.lock
├─ src/
│  ├─ installer/
│  │  └─ install_manager.pyw
│  ├─ runner/
│  │  └─ runner_app.pyw
│  └─ common/
│     ├─ config.py
│     ├─ logging_utils.py
│     └─ recovery.py
├─ logs/
├─ tests/
└─ docs/
   ├─ Docling 변환 프로그램 메뉴얼_2602150743.md
   └─ manual.md
```

---

## 3) 설치 절차 (필수)

### 3.1 사전 준비
1. Python 3.12.x 설치
   - 공식 URL: `https://www.python.org/downloads/windows/`
   - 설치 시 **Add python.exe to PATH** 체크
2. 인터넷 연결 및 디스크 여유 공간 확인
3. GPU 사용 시 NVIDIA/CUDA 호환성 확인

### 3.2 설치 명령어
아래 명령어를 순서대로 실행합니다.

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install psutil pillow
pip install docling
# GPU 사용 시 환경에 맞는 torch 설치 추가
```

---

## 4) 실행 절차 및 실행 명령어 (필수)

### 4.1 GUI 실행
```bash
.venv\Scripts\pythonw.exe src\runner\runner_app.pyw
```

### 4.2 콘솔 디버그 실행(권장)
```bash
.venv\Scripts\python.exe src\runner\runner_app.pyw
```

### 4.3 실행 후 작업
1. 입력(원본 PDF) 폴더 지정
2. 출력 폴더 지정
3. 옵션 설정(강제 OCR/병렬 처리/자동 재시작)
4. 변환 시작
5. 완료 후 `report_manifest.csv` 및 `logs/runtime.log` 확인

---

## 5) 운영 정책

### 5.1 예외 처리
- 금지: `except: pass`
- 필수 패턴:
```python
try:
    ...
except Exception as e:
    logger.exception("작업 실패: %s", e)
    raise
```

### 5.2 프로세스 호출
- 금지: 리스트 인자 + `shell=True` 혼용
- 권장:
```python
subprocess.run([python_exe, "-m", "venv", venv_dir], check=True, shell=False)
```

### 5.3 자동 재시작
- 횟수 제한(예: 3회)
- 재시도 간격 증가(5초 → 15초 → 30초)
- 한도 초과 시 중지 + 사용자 알림

---

## 6) 검증 체크리스트

- [ ] 설치기 기동 확인
- [ ] 설치 실패 시 로그 남김 확인
- [ ] `except: pass` 잔존 여부 점검
- [ ] `shell=True` 사용 근거 점검
- [ ] 자동 재시작 루프 방지 제한 점검
- [ ] 문서 절차/실행 동작 정합성 점검

---

## 7) 장애 대응

### 설치 무반응
- Python 연결 프로그램 확인
- PATH 설정 확인
- `logs/installer.log` 확인

### 반복 크래시
- 재시작 제한 동작 여부 확인
- 실패 파일/옵션/메모리 사용량 분석
- GPU 옵션 OFF로 원인 분리

### 품질 저하
- OCR/스케일 파라미터 조정
- 문제 PDF 격리 후 재처리
