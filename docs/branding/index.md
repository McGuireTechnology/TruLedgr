# TruLedgr Brand Guidelines

## Overview

TruLedgr is a modern personal finance management platform that balances trust and approachability. Our brand identity reflects the intersection of traditional financial reliability with contemporary digital innovation. These guidelines ensure consistent brand representation across all touchpoints.

## Brand Philosophy

Finance apps typically fall into two categories: trust-heavy blues/greens (Mint, QuickBooks) or playful modern tones (YNAB, Monarch). **TruLedgr occupies the middle ground** - serious enough to feel secure, fresh enough to feel modern.

Our brand communicates:
- **Trust & Reliability** - Users feel confident managing their finances
- **Clarity & Transparency** - Complex financial data made simple
- **Modern Accessibility** - Contemporary design that welcomes all users
- **Professional Competence** - Sophisticated tools without intimidation

---

## 1. Color Palette

### Primary Palette (Core Identity)

Our primary colors form the foundation of the TruLedgr visual identity:

**Deep Blue** `#1E2A38`
- **Usage**: Primary navigation, headers, main brand elements
- **Meaning**: Trust, stability, professionalism
- **Role**: Anchor color that grounds the entire palette

**Vibrant Teal** `#00B8A9`
- **Usage**: CTAs, links, interactive elements, progress indicators
- **Meaning**: Modern, energetic, tech-forward
- **Role**: Primary action color that drives engagement

**Warm Gray** `#F4F5F7`
- **Usage**: Backgrounds, borders, disabled states
- **Meaning**: Balance, cleanliness, visual rest
- **Role**: Neutral foundation that reduces visual fatigue

### Accent Palette (Highlights & Actions)

**Sunset Orange** `#FF6F3C`
- **Usage**: Urgent actions, warnings, expense categories
- **Meaning**: Attention, urgency, energy
- **Context**: "Add transaction" buttons, alert states

**Lime Green** `#8BC34A`
- **Usage**: Success states, positive trends, income indicators
- **Meaning**: Growth, positivity, achievement
- **Context**: Budget targets met, positive account balances

**Golden Yellow** `#FFC107`
- **Usage**: Alerts, notifications, highlights, pending states
- **Meaning**: Caution, optimism, attention
- **Context**: Pending transactions, important notices

### Color Usage Guidelines

- **Primary Blue**: Use for brand consistency and trust-building elements
- **Teal**: Reserve for primary actions and interactive states
- **Gray**: Apply liberally for hierarchy and visual breathing room
- **Orange**: Use sparingly for high-priority actions only
- **Green**: Associate with positive financial outcomes
- **Yellow**: Limit to informational highlights and warnings

---

## 2. Typography

Typography in TruLedgr serves dual purposes: ensuring numerical readability and conveying brand personality.

### Display Typography

**Primary: Montserrat**
- **Usage**: Logo, headlines, marketing materials, app headers
- **Characteristics**: Modern, geometric, approachable
- **Weights**: Regular (400), Medium (500), Semibold (600), Bold (700)

**Alternative: Poppins**
- **Usage**: Secondary display option for softer applications
- **Characteristics**: Rounded, friendly, contemporary
- **Use case**: Marketing materials requiring warmth

### Interface Typography

**Primary: Inter**
- **Usage**: Body text, UI elements, dashboards, data tables
- **Characteristics**: Optimized for digital, excellent small-size legibility
- **Strengths**: Superior tabular numerals, wide language support
- **Weights**: Regular (400), Medium (500), Semibold (600)

**Alternative: Roboto**
- **Usage**: Fallback option for broad compatibility
- **Characteristics**: Neutral, familiar, widely supported
- **Use case**: Android-first implementations

### Numerical Typography

**Critical Requirement: Tabular Lining Numerals**
- All financial amounts must use tabular (monospaced) numerals
- Ensures proper decimal alignment in tables and lists
- Both Inter and Roboto provide excellent tabular numeral support

### Typography Hierarchy

```
H1 (Page Titles): Montserrat Semibold 32px
H2 (Section Heads): Montserrat Medium 24px
H3 (Subsections): Montserrat Medium 20px
Body Large: Inter Regular 16px
Body: Inter Regular 14px
Body Small: Inter Regular 12px
Financial Data: Inter Medium 14px (Tabular)
Captions: Inter Regular 11px
```

---

## 3. Logo System

### Logo Concepts

Our logo balances traditional financial symbolism with modern digital aesthetics:

**1. Ledger + Modern Grid**
- Abstract "stacked lines" or "columns" evoking accounting ledgers
- Clean, geometric interpretation of traditional bookkeeping
- Scales well for digital applications

**2. Checkmark + Balance**
- Symbolizes financial clarity and correctness
- Communicates accuracy and verification
- Builds trust through familiar positive associations

**3. Monogram (TL)**
- Geometric design forming recognizable brand mark
- Optimized for app icons and favicons
- Memorable shorthand for the brand

**4. Abstract Growth Symbol**
- Stylized upward arrow embedded in lettering
- Suggests financial progress and improvement
- Subtle integration maintains professional appearance

### Logo Variants

**Primary Wordmark**
- Full "TruLedgr" with custom typography treatment
- Use for main brand applications, website headers
- Minimum size: 120px width for digital, 1" for print

**Icon-Only Mark**
- Monogram "TL" or abstract ledger symbol
- Use for app launchers, favicons, social media avatars
- Minimum size: 24px x 24px

**Horizontal Layout**
- Icon + wordmark in horizontal arrangement
- Use for letterheads, email signatures, footer applications

**Stacked Layout**
- Icon above wordmark for square format requirements
- Use for social media profiles, compact spaces

### Logo Design Principles

**Visual Characteristics:**
- Minimal, geometric, flat design (no gradients in core identity)
- Slight rounding for approachability (avoid cold/sterile banking aesthetics)
- High contrast ratios for accessibility compliance
- Scalable vector format for all applications

**Technical Requirements:**
- Works effectively at 16px favicon size
- Maintains legibility in single color (monochrome)
- Clear contrast against both light and dark backgrounds
- Print-safe at 300 DPI resolution

### Logo Usage Guidelines

**Do:**
- Maintain minimum clear space (equal to height of logo)
- Use approved color combinations only
- Ensure sufficient contrast with background
- Scale proportionally (never stretch or distort)

**Don't:**
- Apply effects, shadows, or gradients to logo
- Place over busy or low-contrast backgrounds
- Modify colors outside approved palette
- Use compressed or pixelated versions

---

## 4. Brand Applications

### Digital Applications
- **Web Interface**: Primary brand colors with generous white space
- **Mobile App**: Icon-focused design with teal accents
- **Marketing Materials**: Montserrat display typography with Inter body text
- **Social Media**: Icon-only mark with consistent color usage

### Print Applications
- **Business Materials**: Monochrome logo options for professional appearance
- **Documentation**: Typography hierarchy for clear information structure
- **Promotional Items**: Single-color applications for cost-effective production

---

## 5. Voice & Tone

**Professional yet Approachable**
- Clear, confident communication without jargon
- Helpful guidance without condescension
- Transparent about complex financial concepts

**Trustworthy & Reliable**
- Consistent messaging across all platforms
- Honest about capabilities and limitations
- Security-first language and positioning

**Modern & Accessible**
- Contemporary language that includes diverse users
- Plain English explanations of financial concepts
- Inclusive design considerations in all communications

---

## Implementation Notes

### Development Considerations
- Implement CSS custom properties for consistent color usage
- Use web fonts with appropriate fallbacks
- Ensure WCAG 2.1 AA compliance for all color combinations
- Test logo legibility across various device scales

### Asset Management
- Maintain vector logo files in SVG format
- Provide PNG alternatives for legacy support
- Document hex codes in design systems
- Version control for brand asset updates

This brand guide ensures TruLedgr maintains a cohesive, trustworthy, and modern identity across all user touchpoints while building confidence in personal financial management.