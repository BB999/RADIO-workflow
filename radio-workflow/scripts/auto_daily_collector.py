#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
時間帯に応じて神威日報系番組を自動選択して文字起こし取得 → GitHub Actions実行
午前中（12時まで）: 神威日報（前日夜の放送）
午後（12時以降）: 神威日報午前（当日朝の放送）
"""

import time
import os
import re
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()


class AutoDailyCollector:
    """時間帯に応じて番組を自動選択する文字起こし収集"""
    
    def __init__(self):
        self.driver = None
        self.github_token = os.getenv('GH-TOKEN')
        
        # 日本時間を取得
        jst = pytz.timezone('Asia/Tokyo')
        self.now_jst = datetime.now(jst)
        
        # 時間帯に応じて番組を選択（午前・午後で判定）
        self.hour = self.now_jst.hour
        if self.hour < 12:
            # 午前中（0時〜11時）は「神威日報」（前日夜の放送）
            self.target_program = "神威日報"
            self.program_time = "前日夜"
            self.prefer_yesterday = True
        else:
            # 午後（12時〜23時）は「神威日報午前」（当日朝の放送）
            self.target_program = "神威日報午前"
            self.program_time = "当日朝"
            self.prefer_yesterday = False
        
        print(f"現在の日本時間: {self.now_jst.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"対象番組: {self.target_program}（{self.program_time}の放送）")
        
        if not self.github_token:
            print("警告: GitHub トークンが設定されていません")
    
    def setup_driver(self):
        """WebDriverを設定"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # GitHub Actions用にヘッドレスモード追加
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.set_capability('goog:loggingPrefs', {
            'performance': 'ALL',
            'browser': 'ALL'
        })
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def find_program_from_notion(self):
        """Notionページから対象番組のZoomリンクを取得"""
        notion_url = os.getenv('NOTION_URL')
        if not notion_url:
            print("エラー: NOTION_URL環境変数が設定されていません")
            return None
        
        try:
            self.setup_driver()
            print(f"\nNotionページから{self.target_program}を検索中...")
            self.driver.get(notion_url)
            time.sleep(5)
            
            # 日付パターン（時間帯に応じて優先順位を変更）
            today = self.now_jst
            yesterday = today - timedelta(days=1)
            
            if self.prefer_yesterday:
                # 昨日の日付を優先（前日夜の神威日報を探すため）
                date_patterns = [
                    f"{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}",
                    f"{today.year}-{today.month:02d}-{today.day:02d}",
                    f"{yesterday.month:02d}-{yesterday.day:02d}",
                    f"{today.month:02d}-{today.day:02d}",
                ]
            else:
                # 今日の日付を優先（当日朝の神威日報午前を探すため）
                date_patterns = [
                    f"{today.year}-{today.month:02d}-{today.day:02d}",
                    f"{yesterday.year}-{yesterday.month:02d}-{yesterday.day:02d}",
                    f"{today.month:02d}-{today.day:02d}",
                    f"{yesterday.month:02d}-{yesterday.day:02d}",
                ]
            
            zoom_link = None
            
            for date_pattern in date_patterns:
                try:
                    # 日付を含む要素を検索
                    date_elements = self.driver.find_elements(
                        By.XPATH, 
                        f"//*[contains(text(), '{date_pattern}')]"
                    )
                    
                    print(f"日付 '{date_pattern}' で {len(date_elements)} 個の要素を発見")
                    
                    # 対象番組を探す
                    elements = []
                    for i, element in enumerate(date_elements[:10]):
                        try:
                            element_text = element.text
                            
                            # 対象番組が含まれているかチェック
                            if self.target_program in element_text:
                                # より正確な番組名判定
                                if self.target_program == "神威日報":
                                    # 「神威日報」を探す場合、「神威日報午前」は除外
                                    if "神威日報午前" in element_text:
                                        print(f"  要素{i+1}: {element_text[:50]}... → スキップ（神威日報午前）")
                                        continue
                                elif self.target_program == "神威日報午前":
                                    # 「神威日報午前」を探す場合、厳密に「午前」が含まれることを確認
                                    if "午前" not in element_text:
                                        print(f"  要素{i+1}: {element_text[:50]}... → スキップ（午前なし）")
                                        continue
                                
                                elements.append(element)
                                print(f"  要素{i+1}: {element_text[:50]}... → {self.target_program}を発見！")
                                break
                        except:
                            continue
                    
                    if elements:
                        element = elements[0]
                        element_text = element.text
                        print(f"\n{self.target_program}を発見: {element_text[:50]}...")
                        
                        # クリック処理（複数の方法を試行）
                        search_text = element_text[:20] if len(element_text) > 20 else element_text
                        clicked = False
                        
                        # 各種クリック方法を試行
                        click_methods = [
                            ("div要素", f"//div[contains(text(), '{search_text}') and (@role='button' or @onclick or contains(@class, 'click') or contains(@class, 'link'))]"),
                            ("aタグ", f"//a[contains(text(), '{search_text}')]"),
                            ("任意要素", f"//*[contains(text(), '{search_text}')]")
                        ]
                        
                        for method_name, xpath in click_methods:
                            if clicked:
                                break
                            try:
                                target_elements = self.driver.find_elements(By.XPATH, xpath)
                                if target_elements:
                                    target_element = target_elements[0]
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
                                    time.sleep(1)
                                    
                                    if method_name == "任意要素":
                                        # 親要素をクリック
                                        parent_element = target_element.find_element(By.XPATH, "..")
                                        self.driver.execute_script("arguments[0].click();", parent_element)
                                    else:
                                        self.driver.execute_script("arguments[0].click();", target_element)
                                    
                                    print(f"  {method_name}クリック成功")
                                    clicked = True
                            except Exception as e:
                                print(f"  {method_name}クリック失敗: {str(e)[:50]}...")
                                continue
                        
                        if not clicked:
                            print("  全てのクリック方法が失敗")
                            continue
                        
                        time.sleep(5)
                        
                        # Zoomリンクを探す
                        page_source = self.driver.page_source
                        current_url = self.driver.current_url
                        print(f"  ページアクセス完了")
                        
                        # Zoomリンクを検索
                        zoom_urls = re.findall(r'zoom\.us/rec[^"\s]*', page_source)
                        
                        # 完全なURLを再構築
                        if zoom_urls:
                            zoom_link = zoom_urls[0]
                            if not zoom_link.startswith('http'):
                                zoom_link = 'https://' + zoom_link
                            print(f"Zoomリンク発見")
                            break
                        else:
                            print("  Zoomリンクが見つかりません")
                        
                except Exception as e:
                    print(f"エラー: {e}")
                    continue
            
            return zoom_link
            
        except Exception as e:
            print(f"Notion検索エラー: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def extract_transcript(self, zoom_url):
        """ZoomURLから文字起こしを抽出"""
        try:
            self.setup_driver()
            print(f"\n文字起こし取得中...")
            self.driver.get(zoom_url)
            time.sleep(5)
            
            # APIから文字起こし取得
            logs = self.driver.get_log('performance')
            
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    if 'Network.responseReceived' in str(message):
                        url = message.get('message', {}).get('params', {}).get('response', {}).get('url', '')
                        if 'transcript' in url.lower() and 'vtt' in url.lower():
                            script = f"return fetch('{url}').then(r => r.text()).catch(() => '');"
                            data = self.driver.execute_script(script)
                            if data and len(data) > 100:
                                return self._parse_vtt_to_text(data)
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"文字起こし取得エラー: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
    
    def _parse_vtt_to_text(self, webvtt):
        """WEBVTTを会話形式に変換"""
        try:
            lines = webvtt.split('\n')
            conversations = []
            current_speaker = ""
            current_text = ""
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if line.isdigit():
                    i += 1
                    if i < len(lines) and '-->' in lines[i]:
                        i += 1
                        if i < len(lines):
                            text = lines[i].strip()
                            if text and ':' in text:
                                speaker, speech = text.split(':', 1)
                                speaker = speaker.strip()
                                speech = speech.strip()
                                
                                if speaker == current_speaker:
                                    current_text += " " + speech
                                else:
                                    if current_speaker and current_text:
                                        conversations.append(f"{current_speaker}: {current_text}")
                                    current_speaker = speaker
                                    current_text = speech
                i += 1
            
            if current_speaker and current_text:
                conversations.append(f"{current_speaker}: {current_text}")
            
            return "\n\n".join(conversations)
            
        except Exception as e:
            return webvtt
    
    def save_transcript_to_file(self, transcript_text):
        """文字起こしをファイルに保存（GitHub Actions用）"""
        with open('transcript.txt', 'w', encoding='utf-8') as f:
            f.write(transcript_text)
        print(f"文字起こしをtranscript.txtに保存しました ({len(transcript_text)}文字)")
        return True
    
    def trigger_github_workflow(self, transcript_text):
        """GitHub Actionsワークフローを実行"""
        if not self.github_token:
            print("GitHub トークンが設定されていないため、ワークフローを実行できません")
            return False
        
        try:
            # GitHub API設定
            owner = "BB999"
            repo = "RADIO-workflow"
            workflow_id = "orchestrator-kamui-daily-radio.yml"
            
            # APIエンドポイント
            url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
            
            # ヘッダー
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.github_token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            # ペイロード
            data = {
                "ref": "main",
                "inputs": {
                    "development-report": transcript_text,
                    "public": False,
                    "gemini-summary": False
                }
            }
            
            print("GitHub Actionsワークフローを開始中...")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 204:
                print("ワークフロー実行成功")
                return True
            else:
                print(f"ワークフロー実行失敗: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return False
                
        except Exception as e:
            print(f"GitHub API エラー: {e}")
            return False


def main():
    """メイン実行"""
    print("=" * 60)
    print("神威日報系番組 自動選択・文字起こし収集・GitHub Actions実行")
    print("=" * 60)
    
    collector = AutoDailyCollector()
    
    try:
        # Step 1: Notionから対象番組のZoomリンクを取得
        print(f"\n[Step 1] {collector.target_program}の録画を検索...")
        zoom_url = collector.find_program_from_notion()
        
        if not zoom_url:
            print(f"\n{collector.target_program}の録画が見つかりませんでした。")
            return
        
        # Step 2: 文字起こしを取得
        print("\n[Step 2] 文字起こしを取得...")
        transcript = collector.extract_transcript(zoom_url)
        
        if not transcript:
            print("文字起こしの取得に失敗しました。")
            return
        
        print(f"文字起こし取得成功 ({len(transcript)}文字)")
        
        # GitHub Actions環境の場合はファイルに保存するだけ
        if os.getenv('GITHUB_ACTIONS'):
            print("\n[Step 3] 文字起こしをファイルに保存...")
            collector.save_transcript_to_file(transcript)
            print("\n文字起こしの取得と保存が完了しました！")
            return
        
        # ローカル環境の場合はワークフローを実行
        print("\n[Step 3] GitHub Actionsワークフローを実行...")
        success = collector.trigger_github_workflow(transcript)
        
        if success:
            print("\n全ての処理が完了しました！")
            print("GitHub Actionsでワークフローが実行されています。")
            print("確認URL: https://github.com/BB999/RADIO-workflow/actions")
        else:
            print("\nワークフローの自動実行に失敗しました。")
            print("手動で実行する場合は、以下のURLから:")
            print("https://github.com/BB999/RADIO-workflow/actions/workflows/orchestrator-kamui-daily-radio.yml")
        
    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    main()