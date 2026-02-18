interface RankMedalProps {
  rank: 1 | 2 | 3;
}

const medalEmoji: Record<1 | 2 | 3, string> = {
  1: '\u{1F947}',
  2: '\u{1F948}',
  3: '\u{1F949}',
};

const medalLabels: Record<1 | 2 | 3, string> = {
  1: 'Gold medal',
  2: 'Silver medal',
  3: 'Bronze medal',
};

export function RankMedal({ rank }: RankMedalProps): JSX.Element {
  return (
    <span className="text-base leading-none" role="img" aria-label={medalLabels[rank]}>
      {medalEmoji[rank]}
    </span>
  );
}
