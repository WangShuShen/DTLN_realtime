# Dual-signal Transformation LSTM Network

## 執行環境
Ubuntu 20.04桌面板
## 步驟
1.For the environment:
```
conda env create -f eval_env.yml
conda activate eval_env
```
2.下載剩餘沒裝到的套件
```
sh install_addition_dependency.sh
```
3.查看使用的設備
```
python real_time_dtln_audio.py --list devices
```
4.1自行選擇輸入/輸出設備執行code
```
python inference_realtime.py -i input_device_id -o output_device_id
```
4.2設定Ubuntu內建的輸入/輸出裝置
輸入設定路徑：Settings -> Sound -> Output -> Output Device
輸出設定路徑：Settings -> Sound -> Input -> Input Device
```
python inference_realtime.py
```
5.按下"Start Recording"，即時播放語音增強的聲音。

6.按下"Stop Recording"，關閉播放聲音。

備註：
1.預設延遲時間都為0.01秒如須額外設定的話，EX:設定延遲時間0.2秒。
```
python inference_realtime.py --latency 0.2
```
2.程式碼內部修改延遲時間，default值改掉即可。
```
parser.add_argument('--latency', type=float,
                    help='latency in seconds', default=0.01)
```
