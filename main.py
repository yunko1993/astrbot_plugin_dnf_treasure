import random
import json
import os
from datetime import datetime
from astrbot.api.event import filter
from astrbot.api.star import Context, Star, register
from astrbot.core.platform import AstrMessageEvent

@register("dnf_treasure_sim", "qingcai", "模拟DNF秘宝精度调试全过程", "1.0.0")
class DnfTreasurePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.db_path = os.path.join("data", "dnf_treasure.json")
        self.data = self._load_db()

    def _load_db(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f: return json.load(f)
            except: return {}
        return {}

    def _save_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    @filter.command("野猪秘宝")
    async def simulate(self, event: AstrMessageEvent):
        user_id = str(event.get_sender_id())
        user_name = event.get_sender_name()
        today = datetime.now().strftime("%Y-%m-%d")

        if user_id in self.data and self.data[user_id] == today:
            yield event.plain_result(f"⚠️ [{user_name}]，今天调试机次数已用完，明天再来！")
            return

        progress, hands, steps_log = 0, 0, []
        checkpoints = [25, 50, 75, 100]
        
        while progress < 100:
            hands += 1
            next_cp = min([c for c in checkpoints if c > progress])
            roll = random.random()
            if roll < 0.03: add, desc = random.randint(20, 25), "🌟 灵光一闪！"
            elif roll < 0.12: add, desc = random.randint(10, 15), "🔥 大成功！"
            elif roll < 0.35: add, desc = random.randint(5, 9), "✨ 顺利"
            elif roll < 0.85: add, desc = random.randint(2, 4), "⚙️ 平稳"
            else: add, desc = 1, "💀 走火..."
            
            if progress + add >= next_cp:
                actual_add = next_cp - progress
                progress = next_checkpoint = next_cp
                status = f"{desc} (🚨 阶段锁定)" if next_cp < 100 else desc
            else:
                actual_add, progress, status = add, progress + add, desc
            steps_log.append(f"第 {hands:2} 手: +{actual_add:2}% (当前 {progress:3}%) {status}")
        
        self.data[user_id] = today
        self._save_db()
        result = [f"💎 DNF野猪秘宝 - 精度调试记录", f"👤 技师：{user_name}", f"🛡️ 装备：侵染万物的灾厄之心", f"--------------------------"]
        result.extend(steps_log)
        result.append(f"--------------------------\n📊 最终结果：{hands} 手点满！\n💻 技术支持：qingcai")
        yield event.plain_result("\n".join(result))