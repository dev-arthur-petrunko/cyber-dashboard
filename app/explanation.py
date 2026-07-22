"""
Rule-based explanation and recommendation generator for threats.

Generates contextual explanations and actionable recommendations based on
threat type, severity, source, and metadata.
"""
from app.models.threat import Threat, ThreatType, Severity


def generate_explanation(threat: Threat) -> dict:
    """
    Generate explanation and recommendations for a threat.
    
    Returns:
        {
            "explanation": str - what this threat is,
            "risk": str - what risk it poses,
            "recommendations": list[str] - actionable steps to mitigate
        }
    """
    explanation = _get_explanation(threat)
    risk = _get_risk(threat)
    recommendations = _get_recommendations(threat)
    
    return {
        "explanation": explanation,
        "risk": risk,
        "recommendations": recommendations,
    }


def _get_explanation(threat: Threat) -> str:
    """Generate explanation of what this threat is."""
    
    # CVE-based threats
    if threat.cve_id:
        cve = threat.cve_id
        if threat.type == ThreatType.exploit:
            return f"Експлойт для вразливості {cve}. Це готовий код або інструмент, який використовує вразливість для компрометації систем."
        elif threat.exploit_maturity == "PoC":
            return f"Proof-of-Concept для вразливості {cve}. Демонстраційний код, що підтверджує можливість експлуатації."
        else:
            return f"Вразливість {cve} з CVSS score {threat.cvss_score or 'N/A'}. Може бути використана зловмисниками для несанкціонованого доступу."
    
    # IoC indicators
    if threat.type == ThreatType.ioc:
        source = threat.source
        if source == "ThreatFox":
            return "Індикатор компрометації (IoC) з бази ThreatFox (abuse.ch). Це IP-адреса, домен або хеш, пов'язаний зі шкідливою активністю."
        elif source == "MalwareBazaar":
            return "Зразок шкідливого програмного забезпечення з MalwareBazaar. Файл виявився малварі за результатами аналізу."
        elif source == "AlienVault OTX":
            return "Індикатор з пульсу AlienVault OTX. Це частина кампанії або звіту про кіберзагрозу."
        else:
            return "Індикатор компрометації, пов'язаний із відомою загрозою."
    
    # News/advisory
    if threat.type == ThreatType.news:
        if "CERT-UA" in (threat.source or ""):
            return "Попередження від CERT-UA про кіберзагрозу, спрямовану на українські організації."
        elif "RNBO" in (threat.source or ""):
            return "Повідомлення від РНБО про кібербезпекову ситуацію в Україні."
        else:
            return "Новина про кіберзагрозу з перевіреного джерела."
    
    # Advisory
    if threat.type == ThreatType.advisory:
        if threat.source == "CISA KEV":
            return f"Вразливість {threat.cve_id or ''} з каталогу CISA Known Exploited Vulnerabilities. Це означає, що є підтверджені випадки її реальної експлуатації зловмисниками."
        return "Рекомендація з кібербезпеки від офіційного джерела."
    
    # Severity-based fallback
    if threat.severity in [Severity.critical, Severity.high]:
        return "Серйозна кіберзагроза, що потребує негайної уваги."
    return "Кіберзагроза, виявлена автоматичними системами моніторингу."


def _get_risk(threat: Threat) -> str:
    """Generate risk description."""
    
    if threat.severity == Severity.critical:
        return "Критичний ризик: можлива повна компрометація систем, втрата даних або фінансові збитки."
    elif threat.severity == Severity.high:
        return "Високий ризик: значна ймовірність компрометації або порушення роботи систем."
    elif threat.severity == Severity.medium:
        return "Помірний ризик: можлива часткова компрометація або порушення конфіденційності."
    elif threat.severity == Severity.low:
        return "Низький ризик: обмежений вплив, але рекомендується вжити заходів."
    return "Ризик не визначено."


def _get_recommendations(threat: Threat) -> list[str]:
    """Generate actionable recommendations."""
    
    recommendations = []
    
    # IoC-specific recommendations
    if threat.type == ThreatType.ioc:
        summary = (threat.summary or "").lower()
        if "domain:" in summary or "domain indicator" in (threat.title or "").lower():
            recommendations.extend([
                "Заблокуйте вказаний домен на DNS-рівні та проксі-серверах",
                "Перевірте логи на наявність запитів до цього домену",
                "Додайте домен до списку заблокованих у файрволах",
            ])
        elif "ip:" in summary or "ip:port indicator" in (threat.title or "").lower():
            recommendations.extend([
                "Заблокуйте вказану IP-адресу на файрволі та IPS/IDS",
                "Перевірте логи на наявність з'єднань з цією IP",
                "Додайте IP до чорного списку мережевих пристроїв",
            ])
        elif "sha256" in summary or "hash" in summary:
            recommendations.extend([
                "Перевірте файли з вказаним хешем на всіх системах",
                "Додайте хеш до списку заблокованих в антивірусі/EDR",
                "Ізолюйте системи, де виявлено файл з таким хешем",
            ])
        elif "url:" in summary:
            recommendations.extend([
                "Заблокуйте вказаний URL на проксі та веб-фільтрах",
                "Перевірте логи веб-проксі на наявність запитів",
                "Попередьте користувачів про фішинговий ресурс",
            ])
        else:
            recommendations.extend([
                "Перевірте системи на наявність індикаторів компрометації",
                "Оновіть сигнатури антивірусу та EDR",
                "Посильте моніторинг мережевого трафіку",
            ])
        
        if "malwarebazaar" in (threat.source or "").lower():
            recommendations.extend([
                "Видаліть зразок малварі з усіх систем",
                "Проведіть повне сканування антивірусом",
                "Перевірте, чи не було запущено цей файл (аналіз процесів)",
            ])
    
    # CVE/exploit recommendations
    elif threat.cve_id or threat.type in [ThreatType.exploit, ThreatType.cve]:
        recommendations.extend([
            "Перевірте, чи використовуються вразливі версії ПЗ",
            "Застосуйте патчі та оновлення безпеки",
            "Використовуйте віртуальний патчинг (virtual patching) як тимчасовий захист",
        ])
        if threat.type == ThreatType.exploit:
            recommendations.extend([
                "Активуйте додаткові правила IDS/IPS для детекції цього експлойту",
                "Моніторте мережу на підозрілу активність",
            ])
        if threat.exploit_maturity == "PoC":
            recommendations.append("Не запускайте PoC-код у продуктивному середовищі")
    
    # CISA KEV
    elif threat.source == "CISA KEV":
        recommendations.extend([
            "Застосуйте патч протягом терміну, вказаного CISA (зазвичай 2 тижні)",
            "Перевірте системи на наявність ознак компрометації",
            "Повідомте CERT-UA про виявлені ознаки експлуатації",
        ])
    
    # News/advisory
    elif threat.type == ThreatType.news:
        recommendations.extend([
            "Ознайомтеся з деталями загрози",
            "Перевірте, чи стосується ця загроза ваших систем",
            "Оновіть заходи захисту відповідно до рекомендацій",
        ])
    
    # Severity-based fallback
    if not recommendations:
        if threat.severity in [Severity.critical, Severity.high]:
            recommendations = [
                "Негайно перевірте системи на ознаки компрометації",
                "Застосуйте доступні патчі та оновлення",
                "Посильте моніторинг та логування",
                "Повідомте CERT-UA про інцидент",
            ]
        else:
            recommendations = [
                "Перевірте системи на наявність вразливостей",
                "Оновіть ПЗ до останніх версій",
            ]
    
    return recommendations[:5]  # Limit to 5 recommendations
