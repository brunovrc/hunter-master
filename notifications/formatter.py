from analysis.score_engine import Recommendation, ScoreReport

ICONS = {
    Recommendation.BUY_NOW: "🟢",
    Recommendation.NEGOTIATE: "🟡",
    Recommendation.FLAG_AUTHENTICATOR: "🔵",
    Recommendation.REFUSE: "🔴",
}

STATUS_ICONS = {"VERDE": "✅", "AMARELO": "⚠️", "VERMELHO": "❌"}


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_telegram(report: ScoreReport) -> str:
    icon = ICONS.get(report.recommendation, "⚪")
    lines = [
        f"<b>{icon} HUNTER MASTER — {_esc(report.recommendation.value)}</b>",
        f"Score: <b>{report.total_score}/100</b>",
        "",
        f"📦 {_esc(report.title)}",
        "",
        f"💰 Compra: R$ {report.buy_price:.0f}",
        f"📈 Venda est.: R$ {report.sell_price_estimate:.0f}",
        f"📊 Margem: <b>{report.gross_margin:.1%}</b>",
    ]

    if report.suggested_offer:
        lines.append(f"🤝 Oferecer: R$ {report.suggested_offer:.0f}")

    lines += ["", "<b>Filtros:</b>"]
    for f in report.filters:
        s = STATUS_ICONS.get(f.status, "❓")
        lines.append(f"{s} {_esc(f.name)}: {f.score}/{f.max_score} — {_esc(f.detail)}")

    if report.red_flags:
        lines += ["", "<b>Red Flags:</b>"]
        for flag in report.red_flags:
            lines.append(f"🚩 {_esc(flag.code)}: {_esc(flag.description)}")

    lines += ["", f"<i>{_esc(report.reasoning)}</i>"]
    return "\n".join(lines)


def format_daily_report(stats: dict) -> str:
    lines = [
        "<b>📊 RELATÓRIO DIÁRIO — Hunter Master</b>",
        "",
        f"🔍 Varridos: {stats.get('scraped', 0)}",
        f"🆕 Novos: {stats.get('new', 0)}",
        f"✨ Oportunidades: {stats.get('opportunities', 0)}",
        "",
        "<b>Por recomendação:</b>",
        f"🟢 COMPRAR: {stats.get('buy', 0)}",
        f"🟡 NEGOCIAR: {stats.get('negotiate', 0)}",
        f"🔵 AUTENTICADOR: {stats.get('flag', 0)}",
        f"🔴 RECUSAR: {stats.get('refuse', 0)}",
    ]
    if stats.get("errors"):
        lines += ["", f"⚠️ Fontes com erro: {', '.join(stats['errors'])}"]
    return "\n".join(lines)


def format_opportunity_email_html(report: ScoreReport, listing_url: str) -> str:
    filter_rows = "".join(
        f"""<tr>
            <td style="padding:8px;border-bottom:1px solid #eee">{f.name}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">{f.score}/{f.max_score}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;
                color:{'#2d7a2d' if f.status=='VERDE' else '#b36b00' if f.status=='AMARELO' else '#c0392b'}">
                {f.status}
            </td>
            <td style="padding:8px;border-bottom:1px solid #eee">{f.detail}</td>
        </tr>"""
        for f in report.filters
    )
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:620px;margin:0 auto;color:#1a1a1a">
        <h2>{report.recommendation.value} — Score {report.total_score}/100</h2>
        <h3 style="font-weight:400">{report.title}</h3>
        <table style="width:100%;border-collapse:collapse;margin:12px 0">
            <tr><td><strong>Preço de compra</strong></td><td>R$ {report.buy_price:.0f}</td></tr>
            <tr><td><strong>Venda estimada</strong></td><td>R$ {report.sell_price_estimate:.0f}</td></tr>
            <tr><td><strong>Margem bruta</strong></td><td>{report.gross_margin:.1%}</td></tr>
        </table>
        <h4>Análise por filtro</h4>
        <table style="width:100%;border-collapse:collapse">
            <tr style="background:#f5f5f5">
                <th style="padding:8px;text-align:left">Filtro</th>
                <th style="padding:8px;text-align:left">Score</th>
                <th style="padding:8px;text-align:left">Status</th>
                <th style="padding:8px;text-align:left">Detalhe</th>
            </tr>
            {filter_rows}
        </table>
        <p style="margin-top:16px"><em>{report.reasoning}</em></p>
        <a href="{listing_url}"
           style="display:inline-block;margin-top:16px;padding:12px 24px;
                  background:#0e1116;color:white;text-decoration:none;border-radius:4px">
            Ver anúncio
        </a>
    </div>
    """
