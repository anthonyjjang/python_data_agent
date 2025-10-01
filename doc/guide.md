# bizMOB Client TypeScript Library Guide

bizMOB 플랫폼의 네이티브 기능을 TypeScript에서 사용할 수 있도록 하는 표준 라이브러리입니다.

## 📋 개요

bizMOB Client Library는 하이브리드 앱에서 네이티브 기능에 접근하기 위한 TypeScript Wrapper입니다.
- **Xross**: 네이티브 API 접근을 위한 핵심 클래스들
- **BzClass**: 인증, 암호화, 다국어 처리를 위한 유틸리티 클래스들

## 📁 라이브러리 구조

```
src/bizMOB/
├── Xross/                    # 네이티브 API 래퍼 클래스
│   ├── Network.ts           # 네트워크 통신
│   ├── Device.ts            # 디바이스 정보
│   ├── File.ts              # 파일 관리
│   ├── System.ts            # 시스템 기능
│   ├── Database.ts          # 데이터베이스
│   ├── Push.ts              # 푸시 알림
│   ├── Storage.ts           # 로컬 저장소
│   ├── Properties.ts        # 설정 관리
│   ├── Window.ts            # UI 컴포넌트
│   ├── App.ts               # 앱 제어
│   ├── Event.ts             # 이벤트 처리
│   ├── Config.ts            # 설정
│   ├── Contacts.ts          # 연락처
│   ├── Logger.ts            # 로깅
│   └── Localization.ts      # 다국어
├── BzClass/                 # 유틸리티 클래스
│   ├── BzToken.ts          # JWT 토큰 관리
│   ├── BzCrypto.ts         # 암호화 통신
│   └── BzLocale.ts         # 다국어 처리
└── i18n/                   # 국제화 설정
    └── index.ts
```

## 🌐 Network (네트워크 통신)

### 기본 사용법
```ts
import Network from '@/bizMOB/Xross/Network';
```

### API 목록

#### `requestTr()` - bizMOB 서버 통신
```ts
const response = await Network.requestTr({
    _sTrcode: 'DM0001',                    // 전문코드
    _oHeader?: Record<string, any>,        // 전문 Header
    _oBody?: Record<string, any>,          // 전문 Body
    _oHttpHeader?: Record<string, any>,    // HTTP Header
    _bProgressEnable?: boolean,            // 프로그레스 표시 여부
    _nTimeout?: number,                    // 타임아웃 (초)
    _bMock?: boolean                       // Mock 데이터 사용 여부
});
```

#### `requestLogin()` - 로그인 통신
```ts
const response = await Network.requestLogin({
    _sUserId: 'user123',                   // 사용자 ID
    _sPassword: 'password',                // 비밀번호
    _sTrcode: 'LOGIN',                     // 전문코드
    _oBody?: Record<string, any>,          // 전문 Body
    _bMock?: boolean
});
```

#### `requestHttp()` - 외부 API 통신
```ts
const response = await Network.requestHttp({
    _sUrl: 'https://api.example.com/data', // 서버 URL
    _sMethod: 'POST',                      // HTTP 메소드
    _oHeader?: Record<string, any>,        // HTTP Header
    _oBody?: Record<string, any>,          // HTTP Body
    _nTimeout?: number
});
```

#### `requestApi()` - 웹 전용 통신
```ts
const response = await Network.requestApi({
    _sMethod: 'GET',                       // HTTP 메소드
    _sUrl: '/api/endpoint',                // 호출 PATH
    _oHeader?: Record<string, any>,        // HTTP Header
    _oBody?: any,                          // HTTP Body
    _nRetries?: number                     // 재시도 횟수
});
```

## 📱 Device (디바이스 정보)

### 기본 사용법
```ts
import Device from '@/bizMOB/Xross/Device';
```

### API 목록

#### 플랫폼 판별
```ts
Device.isApp();        // 앱 환경 여부
Device.isWeb();        // 웹 환경 여부
Device.isMobile();     // 모바일 여부
Device.isPC();         // PC 여부
```

#### OS 판별
```ts
Device.isAndroid();    // Android 여부
Device.isIOS();        // iOS 여부
Device.isTablet();     // 태블릿 여부
Device.isPhone();      // 폰 여부
```

#### 디바이스 정보 조회
```ts
const deviceInfo = Device.getInfo({
    _sKey: 'deviceId'      // 조회할 디바이스 정보 키
});
```

## 📁 File (파일 관리)

### 기본 사용법
```ts
import File from '@/bizMOB/Xross/File';
```

### API 목록

#### 파일 조작
```ts
// 파일 복사
await File.copy({
    _sSourcePath: '/path/source.jpg',      // 원본 경로
    _sTargetPath: '/path/target.jpg'       // 대상 경로
});

// 파일 이동
await File.move({
    _sSourcePath: '/path/source.jpg',      // 원본 경로
    _sTargetPath: '/path/target.jpg'       // 대상 경로
});

// 파일 삭제
await File.remove({
    _aSourcePath: ['/path/file1.jpg', '/path/file2.jpg']  // 삭제할 파일 목록
});
```

#### 파일 정보 조회
```ts
// 파일 존재 여부 확인
const exists = await File.exist({
    _sSourcePath: '/path/file.jpg'
});

// 파일 정보 조회
const fileInfo = await File.getInfo({
    _aFileList: [
        { _sSourcePath: '/path/file.jpg' }
    ]
});
```

#### 파일 업로드/다운로드
```ts
// 파일 업로드
await File.upload({
    _aFileList: [
        {
            _sSourcePath: '/local/path/file.jpg',
            _sFileName: 'uploaded.jpg'
        }
    ]
});

// 파일 다운로드
await File.download({
    _aFileList: [
        {
            _sURI: 'https://server.com/file.jpg',
            _bOverwrite: true,
            _sFileName: 'downloaded.jpg',
            _sDirectory: '/local/download/'
        }
    ],
    _sMode: 'foreground',                  // foreground | background
    _sProgressBar: 'full'                  // off | each | full
});
```

#### 이미지 처리
```ts
// 이미지 리사이즈
await File.resizeImage({
    _aFileList: [{ _sSourcePath: '/path/image.jpg' }],
    _bIsCopy: true,                        // 복사본 생성 여부
    _sTargetDirectory: '/path/resized/',   // 대상 디렉터리
    _nCompressRate: 80,                    // 압축률 (%)
    _nWidth: 800,                          // 너비
    _nHeight: 600                          // 높이
});

// 이미지 회전
await File.rotateImage({
    _sSourcePath: '/path/image.jpg',       // 원본 경로
    _sTargetPath: '/path/rotated.jpg',     // 대상 경로
    _nOrientation: 6                       // EXIF 회전값 (1-8)
});
```

#### 압축 파일 처리
```ts
// 파일 압축
await File.zip({
    _sSourcePath: '/path/folder/',         // 압축할 경로
    _sTargetPath: '/path/archive.zip'      // 압축 파일 경로
});

// 파일 압축 해제
await File.unzip({
    _sSourcePath: '/path/archive.zip',     // 압축 파일 경로
    _sDirectory: '/path/extracted/'        // 압축 해제 경로
});
```

## 💾 Database (데이터베이스)

### 기본 사용법
```ts
import Database from '@/bizMOB/Xross/Database';
```

### API 목록

#### 데이터베이스 연결
```ts
// DB 열기
await Database.openDatabase({
    _sDbName: 'app.db',                    // DB 파일명
    _sDbVersion: '1.0',                    // DB 버전
    _sDisplayName: 'App Database',         // 표시명
    _nEstimatedSize: 5 * 1024 * 1024      // 예상 크기(byte)
});

// DB 닫기
await Database.closeDatabase();
```

#### SQL 실행
```ts
// SQL 실행 (INSERT/UPDATE/DELETE)
await Database.executeSql({
    _sSql: 'INSERT INTO users (name, email) VALUES (?, ?)',
    _aParams: ['John Doe', 'john@example.com']
});

// SQL 조회 (SELECT)
const result = await Database.executeSelect({
    _sSql: 'SELECT * FROM users WHERE id = ?',
    _aParams: [1]
});

// 배치 SQL 실행
await Database.executeBatchSql({
    _aBatchSql: [
        {
            _sSql: 'INSERT INTO users (name) VALUES (?)',
            _aParams: ['User1']
        },
        {
            _sSql: 'INSERT INTO users (name) VALUES (?)',
            _aParams: ['User2']
        }
    ]
});
```

#### 트랜잭션 관리
```ts
// 트랜잭션 시작
await Database.beginTransaction();

try {
    // SQL 실행들...
    await Database.executeSql({...});
    
    // 커밋
    await Database.commitTransaction();
} catch (error) {
    // 롤백
    await Database.rollbackTransaction();
}
```

## 📱 System (시스템 기능)

### 기본 사용법
```ts
import System from '@/bizMOB/Xross/System';
```

### API 목록

#### 미디어 기능
```ts
// 카메라 호출
await System.callCamera({
    _nQuality: 80,                         // 이미지 품질 (0-100)
    _sDirectory: '/camera/',               // 저장 경로
    _bAllowEdit: true                      // 편집 허용 여부
});

// 갤러리 호출
await System.callGallery({
    _nMaxCount: 5,                         // 최대 선택 개수
    _sDirectory: '/gallery/'               // 저장 경로
});
```

#### 통신 기능
```ts
// 전화 걸기
System.callTEL({
    _sPhoneNumber: '010-1234-5678'
});

// SMS 보내기
System.callSMS({
    _sPhoneNumber: '010-1234-5678',
    _sMessage: '안녕하세요!'
});
```

#### 외부 앱 연동
```ts
// 브라우저 열기
System.callBrowser({
    _sUrl: 'https://www.example.com'
});

// 지도 앱 열기
System.callMap({
    _dLatitude: 37.5665,                   // 위도
    _dLongitude: 126.9780,                 // 경도
    _sAddress: '서울시 중구 명동'           // 주소
});
```

#### 위치 정보
```ts
// GPS 위치 조회
const location = await System.getGPS({
    _nTimeout: 10000,                      // 타임아웃 (ms)
    _bHighAccuracy: true                   // 고정밀도 여부
});
```

## 🔔 Push (푸시 알림)

### 기본 사용법
```ts
import Push from '@/bizMOB/Xross/Push';
```

### API 목록

#### 푸시 설정
```ts
// 서버 등록
await Push.registerToServer({
    _sServerUrl: 'https://push.server.com',
    _sAppId: 'com.example.app'
});

// 푸시 키 조회
const pushKey = await Push.getPushKey();

// 배지 카운트 설정
await Push.setBadgeCount({
    _nCount: 5
});
```

#### 알람 관리
```ts
// 알람 설정
await Push.setAlarm({
    _sAlarmId: 'alarm001',                 // 알람 ID
    _sTitle: '미팅 알림',                   // 제목
    _sMessage: '10분 후 미팅이 있습니다.',   // 메시지
    _dAlarmTime: new Date().getTime() + 600000  // 알람 시간
});

// 알람 조회
const alarm = await Push.getAlarm({
    _sAlarmId: 'alarm001'
});
```

#### 메시지 관리
```ts
// 메시지 목록 조회
const messages = await Push.getMessageList({
    _nStartIndex: 0,
    _nCount: 10
});

// 메시지 읽음 처리
await Push.readMessage({
    _sMessageId: 'msg001'
});

// 읽지 않은 메시지 수 조회
const unreadCount = await Push.getUnreadCount();
```

## 💾 Storage & Properties (저장소)

### Storage (임시 저장소)
```ts
import Storage from '@/bizMOB/Xross/Storage';

// 데이터 저장
await Storage.set({
    _sKey: 'userPrefs',
    _sValue: JSON.stringify({ theme: 'dark' })
});

// 데이터 조회
const value = await Storage.get({
    _sKey: 'userPrefs'
});

// 데이터 삭제
await Storage.remove({
    _sKey: 'userPrefs'
});
```

### Properties (영구 저장소)
```ts
import Properties from '@/bizMOB/Xross/Properties';

// 설정 저장
await Properties.set({
    _sKey: 'appSettings',
    _sValue: JSON.stringify({ language: 'ko' })
});

// 설정 조회
const settings = await Properties.get({
    _sKey: 'appSettings'
});

// 다중 설정 저장
await Properties.setList({
    _aList: [
        { _sKey: 'key1', _sValue: 'value1' },
        { _sKey: 'key2', _sValue: 'value2' }
    ]
});
```

## 🪟 Window (UI 컴포넌트)

### 기본 사용법
```ts
import Window from '@/bizMOB/Xross/Window';
```

### API 목록

#### 네이티브 UI 컴포넌트
```ts
// 서명패드 열기
const signature = await Window.openSignPad({
    _sTitle: '서명을 입력하세요',
    _nWidth: 400,
    _nHeight: 200,
    _sDirectory: '/signatures/'
});

// QR/바코드 스캐너 열기
const scanResult = await Window.openCodeReader({
    _sTitle: 'QR코드를 스캔하세요',
    _aCodeType: ['QR_CODE', 'CODE_128']
});

// 파일 탐색기 열기
const selectedFile = await Window.openFileExplorer({
    _sTitle: '파일을 선택하세요',
    _aFileType: ['image/*', 'application/pdf']
});

// 이미지 뷰어 열기
await Window.openImageViewer({
    _aImageList: [
        { _sImagePath: '/path/image1.jpg' },
        { _sImagePath: '/path/image2.jpg' }
    ],
    _nStartIndex: 0
});
```

## 🔧 App (애플리케이션 제어)

### 기본 사용법
```ts
import App from '@/bizMOB/Xross/App';
```

### API 목록

#### 앱 제어
```ts
// 앱 종료
App.exit();

// 스플래시 화면 숨기기
App.hideSplash();

// 타임아웃 설정
await App.setTimeout({
    _nTimeout: 30000                       // 30초
});

// 타임아웃 조회
const timeout = await App.getTimeout();

// 플러그인 호출
const result = await App.callPlugIn({
    _sPluginName: 'CustomPlugin',
    _oParams: { key: 'value' }
});
```

## 🔐 BzToken (JWT 토큰 관리)

### 기본 사용법
```ts
import BzToken from '@/bizMOB/BzClass/BzToken';
```

### API 목록

#### 토큰 초기화
```ts
BzToken.init({
    accessToken: 'eyJhbGciOiJIUzI1NiIs...',
    accessTokenExpTime: '2024-12-31 23:59:59',
    refreshToken: 'eyJhbGciOiJIUzI1NiIs...',
    refreshTokenExpTime: '2025-01-31 23:59:59'
});
```

#### 토큰 관리
```ts
// 토큰 만료 확인
if (BzToken.isTokenExpired()) {
    // 토큰 갱신
    const newTokens = await BzToken.renewToken({
        _bProgressEnable: true
    });
    
    // 새로운 토큰 정보 저장
    console.log(newTokens.accessToken);
}

// 토큰 정보 조회
const accessToken = BzToken.getAccessToken();
const expTime = BzToken.getAccessTokenExpTime();
```

## 🔒 BzCrypto (암호화 통신)

### 기본 사용법
```ts
import BzCrypto from '@/bizMOB/BzClass/BzCrypto';
```

### API 목록

#### 암호화 초기화
```ts
// 저장된 암호화 정보로 초기화
BzCrypto.init({
    crySymKey: 'stored_sym_key',
    cryAuthToken: 'stored_auth_token',
    cryAuthTokenExpTime: '2024-12-31 23:59:59',
    cryRefreshToken: 'stored_refresh_token',
    cryRefreshTokenExpTime: '2025-01-31 23:59:59'
});
```

#### 암호화 키 관리
```ts
// 새로운 암호화 키 발급
if (BzCrypto.isTokenRequired()) {
    try {
        const cryptoInfo = await BzCrypto.shareAuthKey({
            _bProgressEnable: true
        });
        
        // 암호화 정보 저장 (예: Vuex Store)
        store.dispatch('setCryptoInfo', cryptoInfo);
    } catch (error) {
        console.error('암호화 키 발급 실패:', error);
    }
}

// 암호화 토큰 갱신
if (BzCrypto.isTokenExpired()) {
    try {
        const cryptoInfo = await BzCrypto.renewAuthToken();
        store.dispatch('setCryptoInfo', cryptoInfo);
    } catch (error) {
        console.error('암호화 토큰 갱신 실패:', error);
        // BM4002TKER1002 에러시 새로운 키 발급 필요
        if (error === 'BM4002TKER1002') {
            await BzCrypto.shareAuthKey();
        }
    }
}
```

#### 암호화 정보 조회
```ts
const symKey = BzCrypto.getSymKey();                           // 암호화 키
const authToken = BzCrypto.getCryAuthToken();                  // 인증 토큰
const expTime = BzCrypto.getCryAuthTokenExpTime();             // 만료 시간
```

## 🌐 BzLocale (다국어 처리)

### 기본 사용법
```ts
import BzLocale from '@/bizMOB/BzClass/BzLocale';
```

### API 목록

#### 다국어 관리
```ts
// 다국어 초기화 (앱 시작시)
await BzLocale.initLocale();

// 언어 변경
BzLocale.changeLocale('ko-KR');     // 한국어
BzLocale.changeLocale('en-US');     // 영어

// 현재 언어 조회
const locale = await BzLocale.getLocale();
console.log(locale.locale);         // 'ko-KR'
```

## 📝 이벤트 처리

### Event 클래스
```ts
import Event from '@/bizMOB/Xross/Event';

// 이벤트 등록
Event.setEvent('ready', () => {
    console.log('앱 준비 완료');
});

Event.setEvent('pause', () => {
    console.log('앱 일시정지');
});

Event.setEvent('resume', () => {
    console.log('앱 재개');
});

// 이벤트 해제
Event.clearEvent('ready');
```

## 🔧 Config & Logger

### Config (설정 관리)
```ts
import Config from '@/bizMOB/Xross/Config';

// 설정 저장
Config.set('category', 'key', {
    param1: 'value1',
    param2: 'value2'
});

// 설정 조회
const config = Config.get('category', 'key');
```

### Logger (로깅)
```ts
import Logger from '@/bizMOB/Xross/Logger';

Logger.info('정보 메시지');
Logger.log('일반 로그');
Logger.warn('경고 메시지');
Logger.debug('디버그 정보');
Logger.error('에러 메시지');
```

## ⚠️ 에러 코드 참조

### JWT 토큰 관련
- **ERR000**: Access Token 검증 실패 → `BzToken.renewToken()` 호출
- **BM4002TKER1001**: 유효하지 않은 토큰
- **BM4002TKER1002**: Refresh Token 만료 → 새로운 로그인 필요

### 암호화 통신 관련
- **EAH000**: 암호키 세션 만료 → `BzCrypto.shareAuthKey()` 호출
- **EAH001**: 암호화 인증 토큰 만료 → `BzCrypto.renewAuthToken()` 호출
- **BM4001IMPL0001**: 암호화 키 생성 오류
- **{TRCODE}CRPTEDC001**: 전문 복호화 오류

## 🚀 사용 예제

### 완전한 인증 플로우
```ts
import Network from '@/bizMOB/Xross/Network';
import BzToken from '@/bizMOB/BzClass/BzToken';
import BzCrypto from '@/bizMOB/BzClass/BzCrypto';

class AuthManager {
    async login(userId: string, password: string) {
        try {
            // 암호화 통신 설정 (필요한 경우)
            await this.setupCrypto();
            
            // 로그인 요청
            const response = await Network.requestLogin({
                _sUserId: userId,
                _sPassword: password,
                _sTrcode: 'LOGIN',
                _oBody: { userId, password }
            });
            
            if (response.result) {
                // JWT 토큰 설정
                BzToken.init({
                    accessToken: response.accessToken,
                    accessTokenExpTime: response.accessTokenExpTime,
                    refreshToken: response.refreshToken,
                    refreshTokenExpTime: response.refreshTokenExpTime
                });
                
                return response.body;
            }
            
            throw new Error(response.error_code);
        } catch (error) {
            console.error('로그인 실패:', error);
            throw error;
        }
    }
    
    private async setupCrypto() {
        if (process.env.VUE_APP_ENCRYPTION_USE === 'true') {
            if (!BzCrypto.isInit()) {
                BzCrypto.init({
                    crySymKey: null,
                    cryAuthToken: null,
                    cryAuthTokenExpTime: null,
                    cryRefreshToken: null,
                    cryRefreshTokenExpTime: null
                });
            }
            
            if (BzCrypto.isTokenRequired()) {
                await BzCrypto.shareAuthKey();
            }
        }
    }
}
```

### 파일 업로드 with Progress
```ts
import File from '@/bizMOB/Xross/File';
import System from '@/bizMOB/Xross/System';

class FileManager {
    async selectAndUploadImage() {
        try {
            // 갤러리에서 이미지 선택
            const galleryResult = await System.callGallery({
                _nMaxCount: 1,
                _sDirectory: '/temp/'
            });
            
            if (galleryResult.result && galleryResult.body.length > 0) {
                const selectedFile = galleryResult.body[0];
                
                // 이미지 리사이즈 (선택사항)
                await File.resizeImage({
                    _aFileList: [{ _sSourcePath: selectedFile.filePath }],
                    _bIsCopy: true,
                    _sTargetDirectory: '/temp/resized/',
                    _nCompressRate: 80,
                    _nWidth: 800,
                    _nHeight: 600
                });
                
                // 파일 업로드
                const uploadResult = await File.upload({
                    _aFileList: [{
                        _sSourcePath: '/temp/resized/' + selectedFile.fileName,
                        _sFileName: `upload_${Date.now()}.jpg`
                    }]
                });
                
                return uploadResult;
            }
        } catch (error) {
            console.error('파일 업로드 실패:', error);
            throw error;
        }
    }
}
```

## 📖 참고사항

### Mock 데이터 사용
- 모든 API는 `_bMock: true` 옵션으로 Mock 데이터 사용 가능
- Mock 데이터 위치: `public/mock/bizMOB/**/*.json`

### 에러 처리
- Promise 기반 API는 적절한 try-catch 구문 사용
- 에러 코드에 따른 분기 처리 필요

### 타입 안전성
- 모든 매개변수는 TypeScript 타입 정의 제공
- IDE의 자동완성과 타입 검사 활용

이 가이드는 bizMOB Client Library의 주요 기능을 다루며, 실제 프로젝트에서 네이티브 기능을 효과적으로 활용할 수 있도록 도와줍니다.