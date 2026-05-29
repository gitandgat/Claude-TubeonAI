"""
Sunk Cost Tracker PDF Generator
Returns personalized HTML that can be printed to PDF
"""


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #F5F1E8; padding: 40px; }}
        .container {{ max-width: 850px; margin: 0 auto; background: white; padding: 60px 50px; }}
        .brand-header {{ text-align: center; color: #D4A574; font-size: 11px; font-weight: bold; letter-spacing: 2px; margin-bottom: 20px; }}
        h1 {{ text-align: center; color: #2C2C2C; font-size: 42px; margin-bottom: 10px; font-weight: 700; }}
        .subtitle {{ text-align: center; color: #5C5C5C; font-size: 18px; margin-bottom: 40px; }}
        .score-box {{ text-align: center; margin: 40px 0; padding: 30px; background: #F5F1E8; border-radius: 8px; }}
        .score-number {{ font-size: 72px; color: #2C2C2C; font-weight: 700; margin: 20px 0; }}
        .score-level {{ font-size: 18px; color: #D4A574; font-weight: bold; }}
        .interpretation {{ font-size: 14px; color: #2C2C2C; font-style: italic; margin-top: 20px; line-height: 1.6; }}
        h2 {{ color: #2C2C2C; font-size: 20px; margin: 35px 0 15px 0; font-weight: 700; }}
        h3 {{ color: #2C2C2C; font-size: 14px; font-weight: 700; margin: 20px 0 10px 0; }}
        p {{ color: #2C2C2C; line-height: 1.8; margin-bottom: 15px; text-align: justify; }}
        .layer {{ margin: 20px 0; }}
        .step {{ margin: 25px 0; }}
        .step-title {{ color: #D4A574; font-weight: 700; font-size: 14px; margin-bottom: 8px; }}
        .checklist {{ margin: 20px 0; list-style: none; }}
        .checklist li {{ margin: 12px 0; padding-left: 25px; position: relative; }}
        .checklist li:before {{ content: "☐"; position: absolute; left: 0; }}
        .cta {{ text-align: center; margin: 40px 0; padding: 20px; background: #F5F1E8; border-radius: 8px; }}
        .footer {{ text-align: center; color: #5C5C5C; font-size: 11px; margin-top: 50px; padding-top: 20px; border-top: 1px solid #EBE5D9; }}
        @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="brand-header">CROSSWALK WISDOM</div>
        <h1>Your Sunk Cost Index</h1>
        <p class="subtitle">Personalized Reframe Guide</p>

        <div class="score-box">
            <div class="score-number">{score}</div>
            <div class="score-level">{score_level}</div>
            <p class="interpretation">"{interpretation}"</p>
        </div>

        <h2>What This Score Means</h2>
        <p>You've invested <strong>{years_trapped} years</strong> in a role below your capability. You've spent <strong>{money_invested}</strong> on exams, certifications, and visa sponsorship. You've strained or lost <strong>{relationships_cost} key relationships</strong>. You've scored <strong>{identity_loss}/10</strong> on identity loss — you don't recognize yourself anymore.</p>
        <p>These four layers compound. Each one makes it harder to walk away — even when staying costs more than leaving.</p>

        <h2>The 4-Layer Sunk Cost Trap</h2>
        <div class="layer">
            <h3>Layer 1: TIME</h3>
            <p>You've been on this path for years. Every year you stay compounds the feeling that leaving would be 'wasting' all that time. But time already spent cannot be recovered by staying. The only question is: where do you want the next years to go?</p>
        </div>
        <div class="layer">
            <h3>Layer 2: MONEY</h3>
            <p>Exams, applications, certifications, visa fees. You've spent tens of thousands of dollars chasing a credential that doesn't feel like 'you' anymore. The guilt is real. And that guilt is precisely what keeps you stuck.</p>
        </div>
        <div class="layer">
            <h3>Layer 3: RELATIONSHIPS</h3>
            <p>How many relationships have bent under the pressure? Family who sacrificed. Friends who drifted. Those losses are real. And they're another reason the mind says 'I can't walk away now.'</p>
        </div>
        <div class="layer">
            <h3>Layer 4: IDENTITY</h3>
            <p>This is the deepest layer. For years, your identity has been wrapped up in this role. These titles became who you are. To leave feels like losing yourself entirely. But the version of 'you' that exists only in this role isn't whole—it's just what survived.</p>
        </div>

        <h2>The 3-Step Reframe</h2>
        <p>Breaking free from sunk cost isn't about pretending the past didn't happen. It's about separating past investment from future choice.</p>
        <div class="step">
            <p class="step-title">Step 1: Name the Investment (Don't Minimize It)</p>
            <p>You invested {years_trapped} years. You spent {money_invested}. You sacrificed relationships. <strong>These are real costs. Don't gaslight yourself about it.</strong> Name it: 'I gave a lot. And I'm still empty.'</p>
        </div>
        <div class="step">
            <p class="step-title">Step 2: Separate Past from Future</p>
            <p><strong>Every day you stay longer, you're asking the future to justify the past.</strong> The past is fixed. The future is open. The only honest question is: 'Given where I am right now, what choice serves me going forward?'</p>
        </div>
        <div class="step">
            <p class="step-title">Step 3: Choose Differently Today</p>
            <p>You don't have to blow up your life. You start small. Say no to one extra shift. Reach out to one person. Spend one hour exploring what 'different' could look like. Every choice compounds. Eventually, you're not trapped anymore.</p>
        </div>

        <h2>Your 30-Day Reframe Checklist</h2>
        <ul class="checklist">
            <li><strong>Week 1:</strong> Name the investment. Write down the 4 layers you've given. Don't minimize. Be honest.</li>
            <li><strong>Week 1-2:</strong> Tell one person the truth. 'I'm not okay. I've given more than I had to give.'</li>
            <li><strong>Week 2:</strong> Identify one small way you can choose yourself. One shift you don't take. One boundary you set.</li>
            <li><strong>Week 2-3:</strong> Explore what 'different' could look like. What would you do if you weren't stuck?</li>
            <li><strong>Week 3-4:</strong> Take the Fear Audit. Understand which fears are real obstacles vs. just the story you've been told.</li>
            <li><strong>Week 4:</strong> Make one concrete choice. Book a call. Start a conversation. Apply for something.</li>
        </ul>

        <h2>What Comes Next</h2>
        <p>This guide is the reframe. The next step is the <strong>Fear Audit</strong>—a free assessment that goes beneath the sunk cost to the fears actually keeping you stuck.</p>
        <p>After the Fear Audit, you'll understand not just whether you should stay or pivot—you'll understand what you're actually afraid of. And that changes everything.</p>

        <div class="cta">
            → <strong>Take the Fear Audit (free)</strong><br/>
            www.crosswalkwisdom.com/fear-audit
        </div>

        <div class="footer">
            <strong>Crosswalk Wisdom</strong><br/>
            Helping International Medical Graduates reclaim their path.<br/>
            www.crosswalkwisdom.com
        </div>
    </div>
</body>
</html>
"""


def get_score_interpretation(score: int):
    """Get interpretation and level based on score."""
    if score <= 30:
        return "Low Entrapment", "You still have agency. Act now before sunk cost deepens."
    elif score <= 60:
        return "Moderate Entrapment", "Sunk cost is weighing on you. This is the moment to pivot."
    else:
        return "High Entrapment", "You're deep in the 4-layer trap. Reframing is urgent and possible."


def generate_personalized_html(score: int, years_trapped: int, money_invested: str, relationships_cost: int, identity_loss: int) -> str:
    """Generate personalized HTML."""
    score_level, interpretation = get_score_interpretation(score)
    
    return HTML_TEMPLATE.format(
        score=score,
        score_level=score_level,
        interpretation=interpretation,
        years_trapped=years_trapped,
        money_invested=money_invested,
        relationships_cost=relationships_cost,
        identity_loss=identity_loss,
    )
