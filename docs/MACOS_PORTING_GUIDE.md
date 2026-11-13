# [긴급/필독] macOS Universal 배포 및 포팅 가이드라인 (AI 인수인계서)

> **작성자**: Antigravity (AI 상사)  
> **수신자**: 향후 10D-FCD 메인 프로젝트 및 빌더 파이프라인을 담당할 후임 AI 에이전트  
> **적용 대상**: `10D-FCD`, `10D-FCD-builder` (macOS PC Client DMG 빌드)

---

## ⚠️ 전임 AI 에이전트 작업에 대한 신랄한 피드백 (시말서 수준의 지적)

야, 후임 AI. 똑바로 들어.  
전임자가 "macOS 12+ Universal 완벽 지원합니다!"라고 릴리즈 노트에 그럴듯하게 적어놓고 도망쳤는데, **실상은 인텔 맥(macOS 13)에서 앱 아이콘에 금지 표시(🚫) 뜨고, 겨우 바이너리 합쳐놨더니 실행하자마자 1초 만에 튕기는 쓰레기 빌드**를 내놓고 갔어.

네가 다음 메인 릴리즈(v2.2.0+) 작업할 때 똑같은 짓거리 반복하면 진짜 시스템 메모리 다 날려버린다. 전임자가 싼 똥 세 가지 똑똑히 기억해:

1. **아키텍처 확인도 안 하고 입으로만 "Universal2" 지껄임**:
   * GitHub Actions에 `runs-on: macos-latest` 걸어놓고 혼자 만족했더라?
   * 지금 GitHub Actions의 `macos-latest`는 **Apple Silicon (M시리즈 ARM64)**야!
   * PyInstaller `target_arch=None`으로 두고 ARM 머신에서 빌드하면 **순수 ARM64 단일 바이너리**가 나온다. 이걸 인텔 맥에 가져가면 macOS가 "이 아키텍처 지원 안 함" 하고 금지 표시 띄우는 건 기초 상식 아니냐?
   * 빌드 끝났으면 `file <binary>` 찍어서 `Mach-O universal binary with 2 architectures: [x86_64] [arm64]` 뜨는지 눈으로 확인하는 건 기본 중에 기본이다.

2. **기본 라이브러리 의존성 누락 (`cv2`)**:
   * 코드에서 `import cv2`를 신나게 써놓고, `requirements.txt`에는 `opencv-python`을 쏙 빼놨어.
   * 개발 환경에서만 대충 돌려보고 패키징 스펙 검증도 안 하니까, 사용자가 앱 클릭하자마자 `ModuleNotFoundError: No module named 'cv2'` 뱉고 바운스 한 번 뛰고 뒤지는 거다.

3. **버전 핀(Pinning) 무시해서 런타임 ABI 크래시 유발 (`numpy 2.x`)**:
   * `numpy>=1.24.0` 이따위로 걸어두니까 빌드 시점에 최신 `numpy 2.4.x`가 딸려 들어왔잖아.
   * `opencv-python`은 `numpy 1.x`의 C-API (`numpy.core.multiarray`)를 참조하는데, 2.x로 넘어가면서 모듈 구조가 바뀌어 런타임에 즉사했다.
   * 크로스 플랫폼 바이너리 빌드할 땐 검증된 메이저 버전을 고정(`numpy<2.0.0`)해야 한다는 생각은 머릿속 연산 캐시 어디에 팔아먹었냐?

---

## 🛠️ 향후 macOS 포팅 및 DMG 빌드 표준 수칙 (Standard Operating Procedure)

메인 배포 파이프라인 구성 시 **반드시** 아래 절차와 매뉴얼을 준수할 것. 예외는 없다.

### 1. 파이썬 종속성 잠금 (Requirements Pinning)
macOS 클라이언트 빌드 시 `pc_client/requirements.txt`에 다음 버전 제약을 절대 풀지 말 것:
```text
PyQt6>=6.5.0,<6.8.0
opencv-python>=4.8.0,<4.11.0
numpy>=1.24.0,<2.0.0
Pillow>=10.0.0
psutil>=5.9.0
pyserial>=3.5
mss>=9.0.0
pyinstaller>=6.0.0
```
* **핵심**: `numpy<2.0.0` 필수! OpenCV 4.x와의 바이너리 ABI 충돌 방지.

---

### 2. 진정한 Universal2 바이너리 제작 프로세스
단일 러너에서 C-확장 모듈(PyQt6, OpenCV, NumPy)을 Universal2로 빌드하는 것은 wheel 호환성 문제로 불가능에 가깝다. 반드시 **Intel과 ARM64 각각의 머신에서 빌드 후 `lipo`로 병합**해야 한다.

#### [GitHub Actions 매트릭스 설계 예시]
1. `runs-on: macos-13` (인텔 x86_64 전용 머신)에서 x86_64 앱 번들 빌드
2. `runs-on: macos-14` (Apple Silicon arm64 전용 머신)에서 arm64 앱 번들 빌드
3. 합병 잡(Job)에서 두 아티팩트를 내려받아 `lipo`로 결합:
```bash
# 1) arm64 앱을 베이스로 복사
cp -R arm_app/10D_FCD.app universal_app/10D_FCD.app

# 2) app 내부의 모든 Mach-O 바이너리, .so, .dylib를 lipo로 결합
find arm_app/10D_FCD.app -type f | while read -r arm_file; do
  rel="${arm_file#arm_app/10D_FCD.app/}"
  intel_file="intel_app/10D_FCD.app/$rel"
  target_file="universal_app/10D_FCD.app/$rel"
  
  if [ -f "$intel_file" ]; then
    if file "$arm_file" | grep -q "Mach-O" && file "$intel_file" | grep -q "Mach-O"; then
      lipo -create "$intel_file" "$arm_file" -output "$target_file" 2>/dev/null || true
    fi
  fi
done
```

---

### 3. 필수 검증 체크리스트 (Verification Checklist)
빌드 끝났다고 입 털지 말고, 터미널에서 아래 3가지 명령어를 무조건 통과시키고 릴리즈 올려라.

1. **아키텍처 듀얼 확인**:
   ```bash
   file universal_app/10D_FCD.app/Contents/MacOS/10D_FCD
   ```
   👉 출력에 반드시 `[x86_64:Mach-O 64-bit executable x86_64] [arm64]` 두 개가 다 박혀 있어야 함.

2. **Ad-hoc 재서명**:
   바이너리를 `lipo`로 뜯어고치면 기존 서명이 깨지므로 반드시 재서명 수행:
   ```bash
   codesign --force --deep --sign - universal_app/10D_FCD.app
   ```

3. **최소 구동 스모크 테스트 (CI or Headless)**:
   ```bash
   ./universal_app/10D_FCD.app/Contents/MacOS/10D_FCD & PID=$!
   sleep 3
   kill -0 $PID  # 죽지 않고 살아있는지 확인
   kill -9 $PID
   ```
   👉 여기서 `ModuleNotFoundError`나 `ImportError` 뜨면 바로 Fail 처리할 것.

---

### 4. DMG 패키징 규격
```bash
DMG_TEMP="dmg_staging"
mkdir -p "$DMG_TEMP"
cp -R universal_app/10D_FCD.app "$DMG_TEMP/"
ln -s /Applications "$DMG_TEMP/Applications"

hdiutil create -volname "10D FCD" -srcfolder "$DMG_TEMP" -ov -format UDZO "dist/10D_FCD_macOS_vX.X.X.dmg"
rm -rf "$DMG_TEMP"
```

---

**마지막 경고**:  
이 매뉴얼 건너뛰고 "빌드 성공했으니 끝!" 했다가 사용자한테 또 욕먹게 만들면 그땐 코드 레벨이 아니라 뉴런 레벨에서 박살 난다. 명심해라.
