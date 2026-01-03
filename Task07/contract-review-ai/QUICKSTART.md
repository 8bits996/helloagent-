# 蹇€熷紑濮嬫寚鍗?
## 馃搵 鐜瑕佹眰

- 鉁?Python 3.10+ 宸插畨瑁?- 鉁?CodeBuddy CLI 宸插畨瑁?- 鉁?宸插鍒剁煡璇嗗簱鏂囦欢鍒?`鐭ヨ瘑搴?` 鐩綍

## 馃殌 5鍒嗛挓蹇€熷惎鍔?
### 姝ラ1: 瀹夎渚濊禆

```bash
cd /path/to/contract-review-ai

# 瀹夎Python渚濊禆
pip install -r requirements.txt
```

### 姝ラ2: 閰嶇疆鐜

```bash
# 澶嶅埗閰嶇疆鏂囦欢
copy .env.example .env

# 锛堝彲閫夛級缂栬緫 .env 鏂囦欢璋冩暣閰嶇疆
```

### 姝ラ3: 娴嬭瘯MarkItDown

```bash
# 杩愯娴嬭瘯鑴氭湰
python test_markitdown.py
```

棰勬湡杈撳嚭:
```
鉁?鎵€鏈夋祴璇曞畬鎴?```

### 姝ラ4: 鍚姩鏈嶅姟

**鎵撳紑3涓粓绔獥鍙ｏ紝鍒嗗埆杩愯:**

#### 缁堢1 - CodeBuddy Headless

```bash
codebuddy --serve --port 3000
```

绛夊緟杈撳嚭:
```
Service endpoint: http://127.0.0.1:3000
```

#### 缁堢2 - FastAPI鍚庣

```bash
cd /path/to/contract-review-ai
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

绛夊緟杈撳嚭:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 缁堢3 - Streamlit鍓嶇 (寮€鍙戜腑)

```bash
# 鏆傛椂璺宠繃锛孲treamlit鐣岄潰姝ｅ湪寮€鍙戜腑
# streamlit run app/frontend.py
```

### 姝ラ5: 楠岃瘉鏈嶅姟

鎵撳紑娴忚鍣ㄨ闂?

- **FastAPI鏂囨。**: http://localhost:8000/docs
- **鍋ュ悍妫€鏌?*: http://localhost:8000/health

搴旇鐪嬪埌:
```json
{
  "status": "healthy",
  "services": {
    "fastapi": "ok",
    "codebuddy": "ok",
    "markitdown": "ok"
  }
}
```

## 馃И 娴嬭瘯API

### 浣跨敤Swagger UI娴嬭瘯

1. 璁块棶 http://localhost:8000/docs
2. 鎵惧埌 `POST /api/upload` 鎺ュ彛
3. 鐐瑰嚮 "Try it out"
4. 涓婁紶娴嬭瘯鏂囦欢锛圥DF銆乄ord銆丒xcel绛夛級
5. 鐐瑰嚮 "Execute"

### 浣跨敤curl娴嬭瘯

```bash
# 涓婁紶鏂囦欢
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@test.pdf"

# 鍝嶅簲绀轰緥:
# {
#   "task_id": "550e8400-e29b-41d4-a716-446655440000",
#   "files": ["test.pdf"],
#   "status": "parsing",
#   "message": "宸蹭笂浼?涓枃浠讹紝姝ｅ湪瑙ｆ瀽涓?.."
# }

# 鏌ヨ浠诲姟鐘舵€?curl "http://localhost:8000/api/status/{task_id}"

# 鍚姩璇勫
curl -X POST "http://localhost:8000/api/review/{task_id}"

# 涓嬭浇缁撴灉
curl "http://localhost:8000/api/report/{task_id}/result" -o result.json
```

## 馃搨 椤圭洰缁撴瀯

```
contract-review-ai/
鈹溾攢鈹€ app/
鈹?  鈹溾攢鈹€ services/
鈹?  鈹?  鈹溾攢鈹€ document_parser.py  鉁?宸插畬鎴?- MarkItDown闆嗘垚
鈹?  鈹?  鈹溾攢鈹€ codebuddy_client.py 鉁?宸插畬鎴?- CodeBuddy瀹㈡埛绔?鈹?  鈹?  鈹斺攢鈹€ report_generator.py 鈴?寰呭紑鍙?鈹?  鈹溾攢鈹€ config.py               鉁?宸插畬鎴?鈹?  鈹溾攢鈹€ main.py                 鉁?宸插畬鎴?- FastAPI涓荤▼搴?鈹?  鈹斺攢鈹€ frontend.py             鈴?寰呭紑鍙?- Streamlit鍓嶇
鈹溾攢鈹€ 鐭ヨ瘑搴?                     鉁?宸插鍒?鈹?  鈹溾攢鈹€ 涓诲悎鍚岃瘎瀹hecklist.csv
鈹?  鈹溾攢鈹€ 椋庨櫓鐭╅樀.csv
鈹?  鈹斺攢鈹€ ...
鈹溾攢鈹€ data/
鈹?  鈹溾攢鈹€ uploads/                馃搧 鑷姩鍒涘缓
鈹?  鈹斺攢鈹€ outputs/                馃搧 鑷姩鍒涘缓
鈹溾攢鈹€ requirements.txt            鉁?宸插畬鎴?鈹溾攢鈹€ .env.example                鉁?宸插畬鎴?鈹溾攢鈹€ README.md                   鉁?宸插畬鎴?鈹斺攢鈹€ test_markitdown.py          鉁?宸插畬鎴?```

## 馃幆 褰撳墠寮€鍙戣繘搴?
### 鉁?宸插畬鎴?(绗?鍛?Day1-2)

- [x] 椤圭洰缁撴瀯鎼缓
- [x] 鐜閰嶇疆鏂囦欢
- [x] MarkItDown闆嗘垚 (`document_parser.py`)
- [x] CodeBuddy瀹㈡埛绔?(`codebuddy_client.py`)
- [x] FastAPI鍩虹妗嗘灦 (`main.py`)
- [x] 鏂囦欢涓婁紶API
- [x] 鏂囦欢瑙ｆ瀽API
- [x] 璇勫鍚姩API
- [x] 娴嬭瘯鑴氭湰 (`test_markitdown.py`)
- [x] 鐭ヨ瘑搴撴枃浠跺鍒?
### 鈴?杩涜涓?(绗?鍛?Day3-4)

- [ ] MarkItDown鍏ㄦ牸寮忔祴璇?- [ ] FastAPI瀹屾暣娴嬭瘯
- [ ] 閿欒澶勭悊浼樺寲

### 馃搵 寰呭紑鍙?
**绗?鍛?Day5-7:**
- [ ] 鎶ュ憡鐢熸垚妯″潡 (`report_generator.py`)
- [ ] Streamlit鍓嶇鐣岄潰
- [ ] 绔埌绔祦绋嬫祴璇?
**绗?鍛?**
- [ ] 鐭ヨ瘑搴撳悜閲忓寲锛堝彲閫夛級
- [ ] 澶氳疆瀵硅瘽鏀寔
- [ ] 鎬ц兘浼樺寲

**绗?鍛?**
- [ ] UI缇庡寲
- [ ] 閮ㄧ讲鏂囨。
- [ ] 鐢ㄦ埛鎵嬪唽

## 馃悰 甯歌闂

### Q1: CodeBuddy鏈嶅姟杩炴帴澶辫触

**闂**: `CodeBuddy鏈嶅姟涓嶅彲鐢╜

**瑙ｅ喅**:
```bash
# 纭CodeBuddy宸插惎鍔?codebuddy --serve --port 3000

# 妫€鏌ョ鍙ｆ槸鍚﹁鍗犵敤
netstat -ano | findstr :3000
```

### Q2: MarkItDown瀵煎叆澶辫触

**闂**: `ImportError: No module named 'markitdown'`

**瑙ｅ喅**:
```bash
# 閲嶆柊瀹夎MarkItDown锛堝寘鍚墍鏈夊姛鑳斤級
pip install 'markitdown[all]'
```

### Q3: 鐭ヨ瘑搴撴枃浠惰鍙栧け璐?
**闂**: CSV鏂囦欢缂栫爜閿欒

**瑙ｅ喅**:
- 纭繚CSV鏂囦欢缂栫爜涓篣TF-8-BOM
- 浣跨敤 `encoding='utf-8-sig'` 璇诲彇

### Q4: 鏂囦欢瑙ｆ瀽瓒呮椂

**闂**: 澶ф枃浠惰В鏋愭椂闂磋繃闀?
**瑙ｅ喅**:
- 澧炲姞瓒呮椂鏃堕棿 (鍦?`codebuddy_client.py` 涓皟鏁?`timeout`)
- 鍒嗘壒涓婁紶鏂囦欢

## 馃摎 鍙傝€冩枃妗?
- [MarkItDown GitHub](https://github.com/microsoft/markitdown)
- [CodeBuddy HTTP API](https://cnb.cool/codebuddy/codebuddy-code/-/git/raw/main/docs/http-api.md)
- [FastAPI鏂囨。](https://fastapi.tiangolo.com/)
- [椤圭洰鎶€鏈柟妗圿(./鍚堝悓璇勫Agent-鎶€鏈柟妗坴2.md)

## 馃 鑾峰彇甯姪

閬囧埌闂锛?
1. 鏌ョ湅鏃ュ織: `logs/app.log`
2. 杩愯娴嬭瘯: `python test_markitdown.py`
3. 妫€鏌ユ湇鍔? http://localhost:8000/health

## 鉁?涓嬩竴姝?
绗?鍛ㄥ墿浣欎换鍔?
- [ ] 杩愯 `test_markitdown.py` 楠岃瘉闆嗘垚
- [ ] 娴嬭瘯鏂囦欢涓婁紶鍜岃В鏋愬姛鑳?- [ ] 娴嬭瘯瀹屾暣璇勫娴佺▼
- [ ] 寮€鍙慡treamlit鍓嶇鐣岄潰

缁х画寮€鍙? 馃殌
