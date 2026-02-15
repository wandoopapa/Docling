# Docling

Docling 기반 PDF 변환 시스템 문서 저장소입니다.

## 문서
- 최종 매뉴얼: `docs/Docling 변환 프로그램 메뉴얼_2602150743.md`
- 재검토 보고서(참고): `docs/manual_code_reaudit_20260215.md`
- 문서 인덱스: `docs/manual.md`


## 설치 파일
- 실행 가능한 설치 프로그램: `install_manager.pyw`

- 설치 완료 후 실행 파일(단일): `실행하기(무중단).vbs`

- 설치 로그 파일: 설치 폴더의 `installer_install.log`
- 설치 전 점검: 설치 GUI의 `GPU 사전 점검` 버튼으로 드라이버/CUDA 상태 확인
- 런처 정책: 정상 종료 시 자동 재시작되지 않음, Auto-Recovery OFF 시 재시작 금지
- 복구 판정 상태 파일: `run_state.json` (첫 실행/정상 종료/비정상 종료 구분)

- 최신 안정화(v42.9): stale 복구 토큰 정리, PDF 정렬/0바이트 격리, 저장 실패 검출, GPU 웜업 검사

- 최신 UI(v43.0): 좌측 메뉴에서 인덱싱/설정/업데이트 리스트/격리·실패 목록 페이지를 클릭 전환
