"""
Content Generator for @UnitgroupAI News Bot
Generates clickbait titles, emojis, preview subtitles with validation
"""

import logging
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ContentCategory(Enum):
    """Content categories"""
    MANUFACTURING_NEWS = "manufacturing_news"
    BUSINESS_IDEAS = "business_ideas"
    MACHINERY = "machinery"
    MATERIALS = "materials"
    TRENDS = "trends"


@dataclass
class ClickbaitTitle:
    """Clickbait title option"""
    text: str
    style: str  # "question" | "shocking" | "list" | "how_to" | "number"
    emoji: str
    urgency_level: int  # 1-5
    brand_safe: bool
    appeal_score: int  # 1-10


@dataclass
class EmojiSet:
    """Emoji set for post"""
    title_emoji: str
    section_emojis: Dict[str, str]
    total_count: int
    style: str  # "minimal" | "balanced" | "rich"


@dataclass
class PreviewSubtitle:
    """Preview subtitle under main title"""
    text: str
    length: int
    style: str  # "benefit" | "curiosity" | "urgency" | "exclusivity"
    brand_safe: bool


class ClickbaitGenerator:
    """Generates clickbait titles for news posts"""

    # Title templates by style
    TEMPLATES = {
        "question": [
            "Знаете, почему {subject}?",
            "Что будет, если {subject}?",
            "Как {subject} изменит вашу работу?",
            "Вы готовы к {subject}?",
            "Почему все говорят о {subject}?",
        ],
        "shocking": [
            "{subject} — это революция!",
            "Шокирующее открытие: {subject}",
            "{subject} изменит всё!",
            "Это запретили, но мы узнали: {subject}",
            "Никто не ожидал: {subject}",
        ],
        "list": [
            "ТОП-5 {subject} которые вас удивят",
            "{subject}: полный список 2026",
            "5 способов {subject}",
            "7 фактов о {subject}",
            "Полный гайд: {subject}",
        ],
        "how_to": [
            "Как {subject} за 10 минут",
            "Пошаговое руководство: {subject}",
            "Легкий способ {subject}",
            "Как начать {subject} с нуля",
            "Простая схема {subject}",
        ],
        "number": [
            "{subject} выросла на {number}%",
            "{subject} экономит {number} часов",
            "Заработок от {subject}: {number}k рублей",
            "Производство: +{number}% благодаря {subject}",
            "Брак снизился на {number}%: вот как",
        ],
    }

    # Emoji by category
    CATEGORY_EMOJI = {
        ContentCategory.MANUFACTURING_NEWS.value: "🏭",
        ContentCategory.BUSINESS_IDEAS.value: "💡",
        ContentCategory.MACHINERY.value: "⚙️",
        ContentCategory.MATERIALS.value: "🧪",
        ContentCategory.TRENDS.value: "📈",
    }

    # Forbidden patterns
    FORBIDDEN_PATTERNS = [
        "UNITPLAST" in "title",  # Brand name shouldn't be in title format
        "MINI APP" in "title",  # Hard CTA forbidden
        "КП" in "title",
        "ДЕМО" in "title",
        "КАЛЬКУЛЯТОР" in "title",
        "ЗАЯВКА" in "title",
    ]

    def __init__(self):
        self.generated_titles = []

    def generate_titles(
        self,
        post_content: str,
        category: str,
        num_options: int = 3
    ) -> List[ClickbaitTitle]:
        """
        Generate clickbait title options

        Args:
            post_content: Post body text
            category: Content category
            num_options: Number of options to generate

        Returns:
            List of ClickbaitTitle options
        """
        logger.info(f"Generating {num_options} clickbait titles for {category}")

        # Extract key subject from content
        subject = self._extract_subject(post_content)
        if not subject:
            subject = category.replace("_", " ").title()

        titles = []
        styles = list(self.TEMPLATES.keys())

        for _ in range(num_options):
            style = random.choice(styles)
            emoji = self.CATEGORY_EMOJI.get(category, "📰")

            # Generate title from template
            template = random.choice(self.TEMPLATES[style])
            title_text = template.format(
                subject=subject,
                number=random.choice([20, 50, 75, 100, 300, 500])
            )

            # Capitalize properly
            title_text = self._capitalize_title(title_text)

            # Add emoji to title
            full_title = f"{emoji} {title_text}"

            # Validate brand safety
            is_brand_safe = self._validate_brand_safety(full_title)

            if is_brand_safe:
                titles.append(ClickbaitTitle(
                    text=full_title,
                    style=style,
                    emoji=emoji,
                    urgency_level=self._calculate_urgency(style),
                    brand_safe=True,
                    appeal_score=self._score_appeal(title_text, category)
                ))

        # Sort by appeal score
        titles.sort(key=lambda t: t.appeal_score, reverse=True)

        self.generated_titles.extend(titles)
        return titles[:num_options]

    def _extract_subject(self, text: str) -> Optional[str]:
        """Extract main subject from post content"""
        sentences = text.split(".")
        if sentences:
            # Take first sentence, limit to 10 words
            first_sentence = sentences[0].strip()
            words = first_sentence.split()[:10]
            return " ".join(words).lower()
        return None

    def _capitalize_title(self, title: str) -> str:
        """Properly capitalize Russian title"""
        words = title.split()
        # Capitalize first word and important words
        capitalized = []
        for i, word in enumerate(words):
            if i == 0 or len(word) > 3:
                capitalized.append(word.capitalize())
            else:
                capitalized.append(word)
        return " ".join(capitalized)

    def _validate_brand_safety(self, title: str) -> bool:
        """Validate title against brand safety rules"""
        forbidden_keywords = [
            "MINI APP",
            "КП",
            "ДЕМО",
            "КАЛЬКУЛЯТОР",
            "ЗАЯВКА",
            "РАСЧЁТ",
            "ОТКРЫТЬ",
            "ПОПРОБОВАТЬ",
            "КУПИТЬ"
        ]

        for keyword in forbidden_keywords:
            if keyword in title.upper():
                logger.warning(f"Title contains forbidden keyword: {keyword}")
                return False

        return True

    def _calculate_urgency(self, style: str) -> int:
        """Calculate urgency level (1-5) based on style"""
        urgency_map = {
            "question": 2,
            "shocking": 5,
            "list": 2,
            "how_to": 3,
            "number": 4,
        }
        return urgency_map.get(style, 3)

    def _score_appeal(self, title: str, category: str) -> int:
        """Score appeal of title (1-10)"""
        score = 5  # Base score

        # Add for specificity
        if any(char.isdigit() for char in title):
            score += 2

        # Add for emotional words
        emotional_words = ["шокирующий", "революция", "удив", "запрещ", "никто"]
        if any(word in title.lower() for word in emotional_words):
            score += 1

        # Category-specific adjustments
        if category == ContentCategory.BUSINESS_IDEAS.value:
            score += 1  # Business ideas like higher urgency

        return min(score, 10)


class EmojiSelector:
    """Selects appropriate emoji sets for posts"""

    SECTION_EMOJI_SETS = {
        "results": ["📊", "📈", "✅", "🎯"],
        "price": ["💰", "💵", "📉", "💸"],
        "recommendation": ["✅", "👍", "💡", "🎯"],
        "warning": ["⚠️", "🚨", "❌", "⛔"],
        "process": ["🔄", "⚙️", "🔧", "⚡"],
        "innovation": ["🚀", "💡", "🔬", "✨"],
        "quality": ["✨", "⭐", "💎", "👑"],
        "statistics": ["📊", "📈", "📉", "🔢"],
        "industry": ["🏭", "🏗️", "⚙️", "🔧"],
        "market": ["📊", "💹", "📈", "🎯"],
    }

    def __init__(self):
        self.selected_sets = {}

    def select_emoji_set(
        self,
        post_content: str,
        category: str,
        style: str = "minimal"
    ) -> EmojiSet:
        """
        Select appropriate emoji set for post

        Args:
            post_content: Post text
            category: Content category
            style: "minimal" | "balanced" | "rich"

        Returns:
            EmojiSet with selected emojis
        """
        logger.info(f"Selecting emoji set: style={style}, category={category}")

        # Detect section types in content
        sections = self._detect_sections(post_content)

        # Select emojis for sections
        section_emojis = {}
        for section in sections:
            section_emojis[section] = random.choice(
                self.SECTION_EMOJI_SETS.get(section, ["📝"])
            )

        # Limit emoji count by style
        emoji_counts = {
            "minimal": 3,
            "balanced": 5,
            "rich": 8
        }
        max_emojis = emoji_counts.get(style, 5)

        # Keep only important sections
        if len(section_emojis) > max_emojis:
            important_sections = list(section_emojis.keys())[:max_emojis]
            section_emojis = {s: section_emojis[s] for s in important_sections}

        # Select title emoji
        title_emoji = self._get_category_emoji(category)

        emoji_set = EmojiSet(
            title_emoji=title_emoji,
            section_emojis=section_emojis,
            total_count=len(section_emojis) + 1,  # +1 for title
            style=style
        )

        return emoji_set

    def _detect_sections(self, text: str) -> List[str]:
        """Detect section types in post content"""
        sections = []

        keywords = {
            "results": ["результат", "показ", "улучш", "успех", "вырос"],
            "price": ["цен", "стоим", "инвест", "расход", "экономи"],
            "recommendation": ["рекомендуем", "советуем", "лучше", "выбрать"],
            "warning": ["осторожно", "опасно", "ошибка", "проблема", "риск"],
            "process": ["процесс", "этап", "шаг", "как", "способ"],
            "innovation": ["новый", "революц", "впервые", "инновац", "технолог"],
            "quality": ["качество", "премиум", "люкс", "высокий", "отличный"],
            "statistics": ["данные", "статистик", "факт", "число", "процент"],
        }

        text_lower = text.lower()

        for section, keywords_list in keywords.items():
            if any(kw in text_lower for kw in keywords_list):
                sections.append(section)

        return sections[:5]  # Max 5 sections

    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category"""
        emoji_map = {
            ContentCategory.MANUFACTURING_NEWS.value: "🏭",
            ContentCategory.BUSINESS_IDEAS.value: "💡",
            ContentCategory.MACHINERY.value: "⚙️",
            ContentCategory.MATERIALS.value: "🧪",
            ContentCategory.TRENDS.value: "📈",
        }
        return emoji_map.get(category, "📰")


class PreviewSubtitleGenerator:
    """Generates preview subtitles under main title"""

    SUBTITLE_TEMPLATES = {
        "benefit": [
            "Это экономит {value} часов работы",
            "Прибыль растёт на {value}%",
            "Производство ускорилось в {value} раз",
            "Брак снизился на {value}%",
        ],
        "curiosity": [
            "Вот чем занимаются лидеры индустрии",
            "Это то, что скрывают конкуренты",
            "Редкий взгляд изнутри",
            "Исследование года показало",
        ],
        "urgency": [
            "Сейчас всё меняется",
            "Это случится в Q4 2026",
            "Нужно действовать срочно",
            "Последний день, чтобы успеть",
        ],
        "exclusivity": [
            "Знают только 1% производителей",
            "Это делают только лучшие",
            "Секрет успешных компаний",
            "Внутренняя информация",
        ],
    }

    def generate_subtitle(
        self,
        post_content: str,
        category: str,
        style: str = "benefit"
    ) -> PreviewSubtitle:
        """
        Generate preview subtitle

        Args:
            post_content: Post body text
            category: Content category
            style: "benefit" | "curiosity" | "urgency" | "exclusivity"

        Returns:
            PreviewSubtitle
        """
        logger.info(f"Generating subtitle: style={style}")

        templates = self.SUBTITLE_TEMPLATES.get(style, self.SUBTITLE_TEMPLATES["benefit"])
        template = random.choice(templates)

        # Generate subtitle
        subtitle_text = template.format(value=random.choice([20, 50, 100, "2-3", "10-15"]))

        # Limit length
        if len(subtitle_text) > 80:
            subtitle_text = subtitle_text[:77] + "..."

        return PreviewSubtitle(
            text=subtitle_text,
            length=len(subtitle_text),
            style=style,
            brand_safe=True
        )

    def select_best_subtitle(
        self,
        post_content: str,
        category: str
    ) -> PreviewSubtitle:
        """
        Auto-select best subtitle based on content

        Args:
            post_content: Post body text
            category: Content category

        Returns:
            Best subtitle for this post
        """
        # Determine best style for category
        style_map = {
            ContentCategory.MANUFACTURING_NEWS.value: "benefit",
            ContentCategory.BUSINESS_IDEAS.value: "curiosity",
            ContentCategory.MACHINERY.value: "benefit",
            ContentCategory.MATERIALS.value: "benefit",
            ContentCategory.TRENDS.value: "urgency",
        }

        style = style_map.get(category, "benefit")
        return self.generate_subtitle(post_content, category, style)


class ContentValidator:
    """Validates generated content against brand rules"""

    BRAND_RULES = {
        "forbidden_keywords": [
            "MINI APP",
            "КП",
            "ДЕМО",
            "КАЛЬКУЛЯТОР",
            "РАСЧЁТ",
            "ЗАЯВКА",
            "ОТКРЫТЬ",
            "ПОПРОБОВАТЬ",
        ],
        "forbidden_brands": [
            "UNIFURNITURE",  # Wrong
            "UNIMETALL",  # Wrong
        ],
        "allowed_brands": [
            "UNITFURNITURE",
            "UNITMETALL",
            "UNITPLAST",
            "UNITGROUP",
        ],
    }

    def __init__(self):
        self.validation_log = []

    def validate_title(self, title: str) -> Tuple[bool, str]:
        """
        Validate title

        Args:
            title: Title text

        Returns:
            (is_valid, message)
        """
        title_upper = title.upper()

        # Check forbidden keywords
        for keyword in self.BRAND_RULES["forbidden_keywords"]:
            if keyword in title_upper:
                msg = f"Title contains forbidden keyword: {keyword}"
                self.validation_log.append(msg)
                return False, msg

        # Check forbidden brands
        for brand in self.BRAND_RULES["forbidden_brands"]:
            if brand in title_upper:
                msg = f"Title contains wrong brand name: {brand}"
                self.validation_log.append(msg)
                return False, msg

        # Check length
        if len(title) < 10:
            msg = "Title too short"
            self.validation_log.append(msg)
            return False, msg

        if len(title) > 150:
            msg = "Title too long"
            self.validation_log.append(msg)
            return False, msg

        return True, "Title valid"

    def validate_emoji_set(self, emoji_set: EmojiSet) -> Tuple[bool, str]:
        """Validate emoji set"""
        # Check total count
        if emoji_set.total_count > 10:
            return False, "Too many emojis"

        if emoji_set.total_count < 1:
            return False, "No emojis selected"

        return True, "Emoji set valid"

    def validate_subtitle(self, subtitle: PreviewSubtitle) -> Tuple[bool, str]:
        """Validate subtitle"""
        if len(subtitle.text) < 5:
            return False, "Subtitle too short"

        if len(subtitle.text) > 120:
            return False, "Subtitle too long"

        return True, "Subtitle valid"

    def validate_all(
        self,
        title: str,
        emoji_set: EmojiSet,
        subtitle: PreviewSubtitle
    ) -> Tuple[bool, List[str]]:
        """Validate all content together"""
        messages = []

        title_valid, title_msg = self.validate_title(title)
        if not title_valid:
            messages.append(title_msg)

        emoji_valid, emoji_msg = self.validate_emoji_set(emoji_set)
        if not emoji_valid:
            messages.append(emoji_msg)

        subtitle_valid, subtitle_msg = self.validate_subtitle(subtitle)
        if not subtitle_valid:
            messages.append(subtitle_msg)

        return len(messages) == 0, messages


# ═════════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Example content
    post_content = """
    На европейских фабриках произошла революция. Системы компьютерного
    зрения заменяют людей на контроле качества. Результаты впечатляют:
    точность 95-99%, скорость 5000+ деталей в день, брак упал с 8% на 2%.
    """

    # Generate titles
    title_gen = ClickbaitGenerator()
    titles = title_gen.generate_titles(post_content, "machinery", num_options=3)

    print("Generated Titles:")
    for i, title in enumerate(titles, 1):
        print(f"  {i}. {title.text} (appeal: {title.appeal_score})")

    # Select emoji set
    emoji_gen = EmojiSelector()
    emoji_set = emoji_gen.select_emoji_set(post_content, "machinery", style="minimal")

    print(f"\nEmoji Set: {emoji_set.title_emoji}")
    print(f"  Sections: {emoji_set.section_emojis}")

    # Generate subtitle
    subtitle_gen = PreviewSubtitleGenerator()
    subtitle = subtitle_gen.select_best_subtitle(post_content, "machinery")

    print(f"\nSubtitle: {subtitle.text}")

    # Validate all
    validator = ContentValidator()
    valid, errors = validator.validate_all(titles[0].text, emoji_set, subtitle)

    print(f"\nValidation: {'✅ PASS' if valid else '❌ FAIL'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
