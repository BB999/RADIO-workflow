/**
 * テキストを解析してSSMLのbreakタグを自動挿入する
 */

class SSMLFormatter {
    constructor() {
        // 間の長さ設定（秒）
        this.breakDurations = {
            period: 1.0,        // 句点「。」
            comma: 0.5,         // 読点「、」
            exclamation: 1.2,   // 感嘆符「！」
            question: 1.0,      // 疑問符「？」
            lineBreak: 1.5,     // 改行
            dialogue: 1.3,      // セリフ切り替わり
            ellipsis: 1.5,      // 「……」「…」
            colon: 0.5,         // 「：」
            dash: 0.6           // 「ー」「—」
        };
    }

    /**
     * テキストにSSMLのbreakタグを挿入
     * @param {string} text - 元のテキスト
     * @param {object} options - オプション設定
     * @returns {string} - SSML形式のテキスト
     */
    formatWithBreaks(text, options = {}) {
        // デフォルト設定
        const config = {
            enableLineBreaks: true,     // 改行での間を有効
            enableDialogueBreaks: true, // セリフ切り替わりでの間を有効
            speedMultiplier: 1.0,       // 間の長さの倍率
            ...options
        };

        let result = text;

        // 1. 省略記号「……」「…」の処理
        result = result.replace(/[…]{1,3}/g, (match) => {
            const duration = this.breakDurations.ellipsis * config.speedMultiplier;
            return `<break time="${duration}s" />`;
        });

        // 2. 句読点の処理
        result = result.replace(/。/g, () => {
            const duration = this.breakDurations.period * config.speedMultiplier;
            return `。<break time="${duration}s" />`;
        });

        result = result.replace(/、/g, () => {
            const duration = this.breakDurations.comma * config.speedMultiplier;
            return `、<break time="${duration}s" />`;
        });

        // 3. 感嘆符・疑問符の処理
        result = result.replace(/！/g, () => {
            const duration = this.breakDurations.exclamation * config.speedMultiplier;
            return `！<break time="${duration}s" />`;
        });

        result = result.replace(/？/g, () => {
            const duration = this.breakDurations.question * config.speedMultiplier;
            return `？<break time="${duration}s" />`;
        });

        // 4. コロンの処理
        result = result.replace(/：/g, () => {
            const duration = this.breakDurations.colon * config.speedMultiplier;
            return `：<break time="${duration}s" />`;
        });

        // 5. 改行の処理
        if (config.enableLineBreaks) {
            result = result.replace(/\n/g, () => {
                const duration = this.breakDurations.lineBreak * config.speedMultiplier;
                return `<break time="${duration}s" />`;
            });
        }

        // 6. セリフ切り替わりの検出（「」で囲まれた部分の間）
        if (config.enableDialogueBreaks) {
            result = result.replace(/」(\s*)「/g, (match, whitespace) => {
                const duration = this.breakDurations.dialogue * config.speedMultiplier;
                return `」<break time="${duration}s" />「`;
            });
        }

        // 7. 連続するbreakタグの重複を除去
        result = result.replace(/(<break time="[\d.]+s" \/>)\s*(<break time="[\d.]+s" \/>)/g, (match, break1, break2) => {
            // より長い間の方を採用
            const time1 = parseFloat(break1.match(/time="([\d.]+)s"/)[1]);
            const time2 = parseFloat(break2.match(/time="([\d.]+)s"/)[1]);
            const longerTime = Math.max(time1, time2);
            return `<break time="${longerTime}s" />`;
        });

        return result;
    }

    /**
     * テンポ調整用のプリセット
     */
    getPreset(presetName) {
        const presets = {
            // ゆっくり丁寧
            slow: {
                speedMultiplier: 1.5,
                enableLineBreaks: true,
                enableDialogueBreaks: true
            },
            // 標準
            normal: {
                speedMultiplier: 1.0,
                enableLineBreaks: true,
                enableDialogueBreaks: true
            },
            // テンポよく
            fast: {
                speedMultiplier: 0.7,
                enableLineBreaks: true,
                enableDialogueBreaks: true
            },
            // 非常にテンポよく
            veryFast: {
                speedMultiplier: 0.5,
                enableLineBreaks: false,
                enableDialogueBreaks: true
            }
        };

        return presets[presetName] || presets.normal;
    }

    /**
     * サンプルテキストでのテスト用
     */
    demo() {
        const sampleText = `こんにちは！今日はいい天気ですね。
「そうですね、散歩日和です」
「ところで……あなたは魔法を信じますか？」
「魔法ですか？面白い質問ですね。信じる、信じないというより……」
実際に見たことがあるんです。`;

        console.log('=== 元のテキスト ===');
        console.log(sampleText);
        
        console.log('\n=== 標準テンポ ===');
        console.log(this.formatWithBreaks(sampleText, this.getPreset('normal')));
        
        console.log('\n=== テンポよく ===');
        console.log(this.formatWithBreaks(sampleText, this.getPreset('fast')));
        
        console.log('\n=== 非常にテンポよく ===');
        console.log(this.formatWithBreaks(sampleText, this.getPreset('veryFast')));
    }
}

// 使用例
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SSMLFormatter;
} else {
    // ブラウザ環境での使用例
    const formatter = new SSMLFormatter();
    formatter.demo();
}