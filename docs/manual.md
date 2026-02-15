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

### 3.2 설치 파일 다운로드 및 실행
1. 저장소 루트의 `install_manager.pyw` 파일을 직접 다운로드합니다.
2. 더블클릭 또는 아래 명령으로 실행합니다.
```bash
python install_manager.pyw
```

### 3.3 수동 설치 명령어(대체 경로)
설치 GUI가 아닌 수동 설치가 필요한 경우 아래 명령어를 순서대로 실행합니다.

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

### 4.3 설치 완료 후 실행 파일
- `RUN_DOCLING.bat`
- `실행하기(무중단).vbs`
- `runner_app.pyw` (실제 PDF를 변환하여 .md/.txt 결과를 생성)

### 4.4 실행 파일 무반응 시 즉시 확인
```bash
# 배치파일 우회: 실행기를 직접 실행
.venv\Scripts\pythonw.exe runner_app.pyw

# 오류 확인용 콘솔 실행
.venv\Scripts\python.exe runner_app.pyw
```

### 4.5 실행 후 작업
1. 입력(원본 PDF) 폴더 지정
2. 출력 폴더 지정
3. 옵션 설정(강제 OCR/병렬 처리/자동 재시작)
4. 변환 시작
5. 완료 후 `report_manifest.csv` 및 `logs/runtime.log` 확인


## 4.6 설치 프로그램 무반응 시 즉시 조치

아래 순서대로 진행하세요.

1. **터미널로 강제 실행 확인**
```bash
python install_manager.pyw
```
- 아무 창도 안 뜨면 Python 연결/설치 문제 가능성이 큽니다.

2. **파일 연결 재설정 (Windows)**
- `install_manager.pyw` 우클릭 → 연결 프로그램 → `pythonw.exe` 또는 `python.exe` 지정
- 재실행 후 반응 확인

3. **PATH 확인**
```bash
python --version
where python
```
- 명령이 실패하면 Python 재설치 시 `Add python.exe to PATH`를 다시 체크하세요.

4. **보안 차단 해제**
- 다운로드한 파일 속성에서 "차단 해제" 체크
- 백신/Defender 격리 기록 확인

5. **표준 라이브러리 의존성 원칙 재검증**
- 설치 프로그램 최상단 import에 `psutil`, `torch`, `docling` 등 외부 라이브러리가 있으면 안 됩니다.
- 외부 패키지는 설치 완료 후 실행기에서만 import되도록 분리해야 합니다.

6. **로그 강제 출력 실행(권장)**
```bash
python install_manager.pyw > installer_boot.log 2>&1
```
- 생성된 `installer_boot.log` 첫 오류 줄을 확인하면 원인 추적이 빠릅니다.

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
