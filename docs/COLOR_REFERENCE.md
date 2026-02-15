# Fax Capacitor — Color & Design Reference

> Internal reference for development. Not for end users.

---

## Priority Dot Colors (Queue - leftmost column)

| Priority | Dot Color | Hex | When Used |
|----------|-----------|-----|-----------|
| Critical | 🔴 Red | `#DC2626` | Critical lab values, prior auth denials near appeal deadline |
| High | 🟠 Orange | `#EA580C` | Lab results with abnormals, prior auth decisions |
| Medium | 🟡 Yellow | `#CA8A04` | Referral responses, pharmacy requests, records requests |
| Low | 🟢 Green | `#16A34A` | Insurance correspondence, routine items |
| None | ⚫ Gray | `#9CA3AF` | Marketing/junk |

---

## Document Type Badge Colors

| Type | Color | Hex | Background |
|------|-------|-----|------------|
| Lab Result | Purple | `#7C3AED` | `#7C3AED11` |
| Referral Response | Blue | `#2563EB` | `#2563EB11` |
| Prior Auth | Red | `#DC2626` | `#DC262611` |
| Pharmacy Request | Green | `#059669` | `#05966911` |
| Insurance | Gray | `#6B7280` | `#6B728011` |
| Records Request | Amber | `#D97706` | `#D9770611` |
| Marketing / Junk | Light Gray | `#9CA3AF` | `#9CA3AF11` |
| Unclassified | Blue | `#3B82F6` | `#3B82F611` |

---

## Flag Badge Colors

| Flag | Text Color | Background | Border | Hex Values |
|------|-----------|------------|--------|------------|
| **Incomplete** | Dark Red | Light Red | Red border | text: `#B91C1C`, bg: `#FEF2F2`, border: `#FECACA` |
| **Misdirected** | Purple | Light Purple | Purple border | text: `#7C3AED`, bg: `#F5F3FF`, border: `#DDD6FE` |
| **Bundle** | Dark Amber | Light Yellow | Yellow border | text: `#B45309`, bg: `#FFFBEB`, border: `#FDE68A` |

### Flag vs Type Color Distinction
- **Prior Auth red** (`#DC2626`) ≠ **Incomplete flag red** (`#B91C1C`) — Incomplete is a darker, more muted red
- **Lab Result purple** (`#7C3AED`) = **Misdirected purple** (`#7C3AED`) — Same purple, but flags are styled differently (uppercase, bordered badge vs. filled badge)
- Flags use bordered/outlined style; Types use filled background style — visually distinct even at the same hue

---

## Status Colors

| Status | Color | Hex | Display |
|--------|-------|-----|---------|
| Unreviewed (classified) | Blue | `#2563EB` | "UNREVIEWED" |
| Reviewed | Green | `#16A34A` | "REVIEWED" |
| Flagged | Amber | `#D97706` | "🚩 FLAGGED" |
| Dismissed | Gray | `#9CA3AF` | "DISMISSED" |

---

## Urgency Indicator Badges (Detail Panel)

All urgency indicators use the same style:
- Text: `#DC2626` (red)
- Background: `#FEF2F2` (light red)
- Border: `#FECACA` (red border)
- Uppercase, bold

---

## Confidence Score Colors

| Range | Color | Hex | Meaning |
|-------|-------|-----|---------|
| 90-100% | Green | `#16A34A` | High confidence — reliable |
| 75-89% | Yellow | `#CA8A04` | Moderate — worth verifying |
| Below 75% | Red | `#DC2626` | Low — needs manual review |

---

## Stat Card Accent Colors

| Stat | Accent | Hex |
|------|--------|-----|
| Total Faxes | Default black | `#111827` |
| Unreviewed | Orange | `#EA580C` |
| Urgent | Red | `#DC2626` |
| Reviewed | Green | `#16A34A` |
| Flagged | Amber | `#D97706` |
| Avg Confidence | Blue | `#2563EB` |

---

## Typography

| Element | Font | Weight |
|---------|------|--------|
| Body text | IBM Plex Sans | 400-600 |
| Monospace (confidence, times, phone) | IBM Plex Mono | 400-600 |
| Headers | IBM Plex Sans | 700 |
| Labels (uppercase) | IBM Plex Sans | 600-700 |

---

## Quick Visual Guide

```
Priority dots:  🔴 Critical  🟠 High  🟡 Medium  🟢 Low  ⚫ None

Type badges:    [Lab Result]  [Referral]  [Prior Auth]  [Pharmacy]
                 purple        blue        red           green

                [Insurance]  [Records]  [Marketing]  [Unclassified]
                 gray         amber      light gray    blue

Flag badges:    [INCOMPLETE]  [MISDIRECTED]  [BUNDLE]
                 dark red      purple          dark amber

Status:         UNREVIEWED  REVIEWED  🚩 FLAGGED  DISMISSED
                 blue        green     amber       gray
```
