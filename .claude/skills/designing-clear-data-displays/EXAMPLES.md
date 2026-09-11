# EXAMPLES: Before and After

Sidecar to `SKILL.md`. Six generic pairs; none names a project. Each is a short spec or sketch that shows a kernel rule at work, with a count of what changed. Note pair 5: clear is not always less ink. Decoration shrinks; missing documentation grows into facts.

---

## 1. Two labels that grow toward each other (rule 4)

A board 120 units wide, midline at 60. Two markers 25 units apart. The placement code anchors each label toward the midline so no label runs off the edge: the marker left of the midline gets `text-anchor="start"`, the one right of it gets `end`. At font size 6, a seven-character label spans 23.1 units (0.55 em per glyph).

**Before** (overlap: 15 units at the same baseline):

```svg
<circle cx="50" cy="90" r="3"/>
<text x="55" y="98" font-size="6" text-anchor="start">Block A</text>  <!-- spans 55.0 to 78.1 -->
<circle cx="75" cy="90" r="3"/>
<text x="70" y="98" font-size="6" text-anchor="end">Block B</text>    <!-- spans 46.9 to 70.0 -->
```

The two labels overprint from 55.0 to 70.0 and make a third shape that reads as neither name.

**After** (overlap: none; font unchanged):

```svg
<circle cx="50" cy="90" r="3"/>
<text x="55" y="98" font-size="6" text-anchor="start">Block A</text>  <!-- spans 55.0 to 78.1 -->
<circle cx="75" cy="90" r="3"/>
<text x="80" y="98" font-size="6" text-anchor="start">Block B</text>  <!-- spans 80.0 to 103.1 -->
```

**Rules applied**: 4 (move one, do not shrink both), 3 (nothing shrank).
The first move in rule 4's fix order, flipping one anchor, cleared it with 1.9 units to spare. Shrinking both to font size 4 would have left them overlapping by 15 units, the whole span between the two anchors, and harder to read. No font size clears it; the anchors do.

---

## 2. Numbered markers with a key (rule 2)

**Before** (3 codes, 3 lookups):

> Picture: three marks labeled "1", "2", "3".
> Beside it, a key: "1: Start square. 2: Drop zone. 3: Wall."

Cover the key. The marks name nothing; every read is a dart to the key and back.

**After** (0 codes; the same words in both places):

> Picture: marks labeled "Start", "Drop zone", "Wall".
> Beside it, the setup list: "Start: 30 cm square in the corner. Drop zone: 20 cm square at 50 cm. Wall: 40 cm strip across the far edge."

Cover the list. Every mark still names itself. The list adds the sizes and distances the picture does not carry, and repeats the names so the two agree.

**Rules applied**: 2 (label where it lives), 8 (the caption carries content, not a code).
The words beside the picture were never the fault; the numeral was. A caption that repeats the figure's words is integration. A code that means nothing until decoded is a key.

---

## 3. A truncated axis (rule 5)

Two bars: last year 96, this year 100. Effect in the data: 4.2 percent (100 / 96 = 1.042).

**Before** (lie factor 96):

> Axis from 95 to 100. Bars 1 unit and 5 units tall. Effect shown: 400 percent (5 / 1 = 5.0). Lie factor: 400 / 4.2 = 96.

**After** (lie factor 1.0):

> Axis from 0. Bars 96 and 100 units tall. Effect shown: 4.2 percent. Lie factor: 1.0. Under the chart: "up 4% on last year".

**Rules applied**: 5 (true size), 7 (the axis starts where the reader assumes it does).
If the 4 percent matters and the full axis makes it hard to see, draw a second panel of the difference itself, labeled as a difference. A zoomed axis presented as the whole is the lie; a panel that says "difference" is not.

---

## 4. Six charts, six scales (rule 6)

Six sites, one measure per week over a season.

**Before** (6 axes, 6 scales, 6 titles):

> Six separate charts, each autoscaled. Y-axis tops: 12, 40, 8, 55, 20, 33. Every line fills its box. Site C (top 8) looks as busy as site D (top 55). A reader who wants to compare reads six axes and rescales in their head.

**After** (1 scale, 6 panels, 1 title, 1 axis label):

> A 2 by 3 grid. One y-axis, 0 to 60, on the left column; one x-axis on the bottom row. Each panel carries its site name and nothing else. Site C is a flat line near the floor; site D is a mountain. The comparison is the picture.

**Rules applied**: 6 (compared to what), 1 (five axes and five titles erased).
One panel per case, side by side, on one scale, is small multiples. A fix for crowding must not merge them into one chart with six lines and a key; that trades rule 6 for a rule 2 failure.

---

## 5. No units anywhere (the growing pair, rule 7)

A setup diagram: a square, two circles, and a line on a rectangle.

**Before** (0 units, 0 scale, 0 title):

> Shapes with names on them, nothing else. The reader cannot tell a 10 cm square from a 30 cm square, or whether the board is 1 m or 2 m long.

**After** (1 title, 1 scale bar, 1 unit):

> Title on the figure: "Setup, week 3 (cm)". A scale bar in a corner: a 10-unit rule labeled "10 cm". The board's length printed along its edge: "150 cm".

**Rules applied**: 7 (document the display).
The after carries more ink. Every added mark answers a question the reader had, so it is data-ink. A display that gained ink and gained meaning followed this skill.

---

## 6. Gradients and shadows (rules 1 and 3)

A bar chart on a dark page: five bars, light labels.

**Before**:

> Each bar has a vertical gradient, a drop shadow, and a 3-D bevel. A grid of full-black lines every 5 units. A light panel behind the plot. A key in the corner naming the one series.

**After**:

> Flat bars, one color. Shadows and bevels gone. The grid thinned to a hairline at 20 percent gray, every 20 units. The key gone; the series name is the title. The panel stays: the labels are light and the page is dark, and the panel is the ground that makes them legible.

**Rules applied**: 1 (erase what carries none, within reason), 3 (mute the grid until it just still reads).
Rule 1's "within reason" does the work in the last sentence. The panel stands for no datum; it stays because without it the labels vanish.

---

## See Also

- `RULES.md`: the tests behind each rule applied above.
- `REVIEWING.md`: turning a before-display into a finding with a redraw.
