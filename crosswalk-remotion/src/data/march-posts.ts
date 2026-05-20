import { staticFile } from 'remotion';
import type { AprilPostData } from './april-posts';

const img = (filename: string) => staticFile(`assets/march/${filename}`);

// March 26–31 + May 1 posts — same visual template as April posts
export const MARCH_POSTS: AprilPostData[] = [
  {
    slug: 'mar-26',
    date: '2026-03-26',
    label: 'March 26',
    image: img('mar-26.jpg'),
    hook: 'When I told my mother\nI was leaving medicine, she cried.',
    sub: 'Not because she was sad.\nBecause she was scared for me.',
  },
  {
    slug: 'mar-27',
    date: '2026-03-27',
    label: 'March 27',
    image: img('mar-27.jpeg'),
    hook: 'The metabolic cost\nof staying stuck is real.',
    sub: 'Every year in burnout,\ncortisol stays elevated.',
  },
  {
    slug: 'mar-28',
    date: '2026-03-28',
    label: 'March 28',
    image: img('mar-28.jpg'),
    hook: 'Quitting is not\nthe opposite of success.',
    sub: 'Staying in something that destroys you\nis not strength.',
  },
  {
    slug: 'mar-30',
    date: '2026-03-30',
    label: 'March 30',
    image: img('mar-30.jpeg'),
    hook: "Nobody told me that leaving medicine\nwould feel like a death.",
    sub: 'Not of a career.\nOf an identity.',
  },
  {
    slug: 'mar-31',
    date: '2026-03-31',
    label: 'March 31',
    image: img('mar-31.jpg'),
    hook: "Most people don't leave bad careers\nbecause of logistics.",
    sub: "They leave when they finally name\nwhat they're actually afraid of.",
  },
  {
    slug: 'may-01',
    date: '2026-05-01',
    label: 'May 1',
    image: null,
    hook: 'I wrote everything I wish\nsomeone had told me.',
    sub: 'About the gap between leaving\nand landing.',
  },
];
