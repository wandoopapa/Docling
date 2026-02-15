# Docling 변환 프로그램 매뉴얼 (최종 정리본)

- 문서 버전: **v43.0 (2026-02-15)**
- 기준 문서: `docs/Docling 변환 프로그램 메뉴얼_2602150743.md`
- 목적: 검토 반영이 완료된 설치/운영 표준을 한 문서로 제공

---

## 1) 시스템 개요

본 시스템은 기구 설계 PDF를 LLM 학습용 텍스트 데이터셋으로 변환하는 ETL 도구입니다.

핵심 목표:
1. 재현 가능한 설치
2. 장애 원인 추적 가능한 로그
3. 재시작/복구 정책의 명확한 제어
4. 문서와 실제 동작의 일치

> 설치 GUI는 표준 라이브러리 중심으로 기동할 수 있으나, 실행 엔진은 `docling`, `torch`, `psutil` 등의 외부 패키지 의존성이 있습니다.

---

## 2) 검토 반영 완료 사항

### 2.1 문서 신뢰성
- 복붙형 이스케이프 코드 중심 안내 제거
- 공식 배포 URL 사용(검색 리다이렉트 링크 미사용)
- 버전/이력 관리 방식 명확화(요약 + 변경이력 파일 권장)

### 2.2 설치/운영 안정성
- `shell=True` 남용 금지 (`shell=False` + `check=True` 권장)
- `except: pass` 금지 (`except Exception as e` + 로그 기록 필수)
- 자동 재시작에 횟수 제한/쿨다운 정책 적용

### 2.3 구조 표준화
- 설치기/실행기/공통 모듈 분리
- 로그 파일 영속화(`logs/installer.log`, `logs/runtime.log`)

---

## 3) 권장 프로젝트 구조

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
│  ├─ test_config.py
│  └─ test_recovery.py
└─ docs/
   ├─ Docling 변환 프로그램 메뉴얼_2602150743.md
   └─ manual.md
```

---

## 4) 설치 가이드

### 4.1 사전 준비
1. Python 3.12.x 설치  
   - 공식 URL: `https://www.python.org/downloads/windows/`  
   - 설치 시 **Add python.exe to PATH** 체크
2. 인터넷 연결 및 디스크 여유 공간 확인
3. GPU 사용 시 NVIDIA 드라이버/CUDA 호환성 확인

### 4.2 가상환경 생성
```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
```

### 4.3 의존성 설치(권장 순서)
```bash
pip install psutil pillow
pip install docling
# GPU 필요 시 환경에 맞는 torch 인덱스/버전으로 설치
```

> 운영 환경 재현성을 위해 `requirements.lock` 고정을 권장합니다.

---

## 5) 실행 가이드

1. 입력(원본 PDF) 폴더와 출력 폴더 지정
2. 옵션 설정
   - 강제 OCR
   - 병렬 처리(리소스 상황에 맞춤)
   - 자동 재시작(권장 기본값: OFF)
3. 변환 시작
4. 완료 후 `report_manifest.csv` 및 런타임 로그 확인

---

## 6) 필수 운영 정책

### 6.1 예외 처리 정책
- 금지: `except: pass`
- 권장 패턴:
```python
try:
    ...
except Exception as e:
    logger.exception("작업 실패: %s", e)
    raise
```

### 6.2 프로세스 호출 정책
- 금지: 리스트 인자 + `shell=True` 혼용
- 권장 패턴:
```python
subprocess.run([python_exe, "-m", "venv", venv_dir], check=True, shell=False)
```

### 6.3 자동 재시작 정책
- 최대 재시작 횟수 설정(예: 3회)
- 재시도 간격 점진 증가(예: 5초 → 15초 → 30초)
- 한도 초과 시 중지 후 사용자 알림

---

## 7) 검증 체크리스트

- [ ] 설치기가 표준 라이브러리만으로 기동되는가?
- [ ] 의존성 설치 실패 시 원인 로그가 남는가?
- [ ] `except: pass`가 남아있지 않은가?
- [ ] `shell=True` 사용에 명시적 근거가 있는가?
- [ ] 자동 재시작 루프 방지 제한이 적용되었는가?
- [ ] 문서 절차와 실제 실행 절차가 일치하는가?

---

## 8) 장애 대응

### 8.1 설치 무반응
- Python 연결 프로그램 확인
- PATH 설정 확인
- 설치 로그(`logs/installer.log`) 확인

### 8.2 변환 중 반복 크래시
- 자동 재시작 횟수 제한 동작 여부 확인
- 직전 실패 파일/옵션/메모리 사용량 분석
- GPU 옵션 OFF 재실행으로 원인 분리

### 8.3 결과 품질 저하
- 강제 OCR/스케일 파라미터 조정
- 문제 PDF 격리 후 재처리 큐에서 분리

---

## 9) 버전 이력(요약)

- v43.0: 검토 반영 완료 최종 정리본
- v42.1: 설치기 표준 라이브러리화(무반응 대응)
- v42.0 이하: 기존 기능 이력은 별도 변경이력으로 관리 권장

---

## 10) 결론

본 문서는 검토사항 반영이 완료된 **최종 운영 기준**입니다.
다음 단계는 `src/installer`, `src/runner`, `src/common` 실제 코드 분리와 문서-구현 1:1 정합성 유지입니다.
