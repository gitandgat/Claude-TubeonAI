#!/usr/bin/env python3
"""
Self-Improving AI System - Learns from feedback, auto-tunes parameters, improves over time.
Agents rate their own outputs, user ratings refine thresholds, system optimizes continuously.
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from dotenv import load_dotenv

load_dotenv()

class SelfImprovingSystem:
    """Meta-system that learns from agent performance"""

    def __init__(self):
        self.feedback_log = 'agent-feedback.json'
        self.parameter_log = 'agent-parameters.json'
        self.metrics = {
            'performance': defaultdict(list),
            'accuracy': defaultdict(list),
            'user_ratings': defaultdict(list),
            'improvements': defaultdict(list)
        }
        self.parameters = self.load_parameters()
        self.feedback = self.load_feedback()

    def load_parameters(self):
        """Load current agent parameters"""
        if os.path.exists(self.parameter_log):
            with open(self.parameter_log, 'r') as f:
                return json.load(f)
        else:
            # Default parameters
            return {
                'stop_slop_threshold': 35,
                'duplicate_similarity': 0.85,
                'hashtag_coverage_target': 95,
                'engagement_forecast_confidence': 0.6,
                'archive_days': 90,
                'max_posts_per_hour': 5
            }

    def load_feedback(self):
        """Load feedback history"""
        if os.path.exists(self.feedback_log):
            with open(self.feedback_log, 'r') as f:
                return json.load(f)
        else:
            return {'records': []}

    def save_parameters(self):
        """Save updated parameters"""
        with open(self.parameter_log, 'w') as f:
            json.dump(self.parameters, f, indent=2)

    def save_feedback(self):
        """Save feedback log"""
        with open(self.feedback_log, 'w') as f:
            json.dump(self.feedback, f, indent=2)

    def submit_feedback(self, agent_name, output_id, rating, feedback_text, metrics=None):
        """
        User submits feedback on agent output.
        Rating: 1-10
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'output_id': output_id,
            'rating': rating,
            'feedback': feedback_text,
            'metrics': metrics or {}
        }

        self.feedback['records'].append(record)
        self.metrics['user_ratings'][agent_name].append(rating)
        self.save_feedback()

        # Auto-tune based on feedback
        if rating >= 8:
            self.reinforce_agent(agent_name)
        elif rating <= 4:
            self.improve_agent(agent_name, feedback_text)

        return {'status': 'recorded', 'action_taken': True}

    def reinforce_agent(self, agent_name):
        """Strengthen parameters that worked"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'type': 'reinforce',
            'agent': agent_name,
            'action': 'Parameters kept stable (high-rating strategy)'
        }
        self.metrics['improvements'][agent_name].append(record)

    def improve_agent(self, agent_name, feedback_text):
        """Adjust parameters based on low ratings"""
        adjustments = self.infer_adjustments(agent_name, feedback_text)

        for param, new_value, reason in adjustments:
            old_value = self.parameters.get(param)
            self.parameters[param] = new_value

            record = {
                'timestamp': datetime.now().isoformat(),
                'type': 'adjustment',
                'agent': agent_name,
                'parameter': param,
                'old_value': old_value,
                'new_value': new_value,
                'reason': reason
            }
            self.metrics['improvements'][agent_name].append(record)

        self.save_parameters()

    def infer_adjustments(self, agent_name, feedback_text):
        """Infer parameter adjustments from feedback"""
        adjustments = []
        feedback_lower = feedback_text.lower()

        # Stop-slop threshold
        if 'stop slop' in feedback_lower or 'quality' in feedback_lower:
            if 'too strict' in feedback_lower or 'too many' in feedback_lower:
                adjustments.append((
                    'stop_slop_threshold',
                    self.parameters['stop_slop_threshold'] - 2,
                    'Feedback: threshold too strict, lowering to catch more variations'
                ))
            elif 'not strict' in feedback_lower or 'needs better' in feedback_lower:
                adjustments.append((
                    'stop_slop_threshold',
                    self.parameters['stop_slop_threshold'] + 1,
                    'Feedback: threshold too loose, raising to improve quality'
                ))

        # Duplicate detection
        if 'duplicate' in feedback_lower:
            if 'missing' in feedback_lower:
                adjustments.append((
                    'duplicate_similarity',
                    self.parameters['duplicate_similarity'] - 0.05,
                    'Feedback: duplicates being missed, lowering threshold'
                ))
            elif 'false positive' in feedback_lower:
                adjustments.append((
                    'duplicate_similarity',
                    self.parameters['duplicate_similarity'] + 0.05,
                    'Feedback: false positives, raising threshold'
                ))

        # Archive threshold
        if 'archive' in feedback_lower:
            if 'too old' in feedback_lower:
                adjustments.append((
                    'archive_days',
                    self.parameters['archive_days'] + 30,
                    'Feedback: archiving too early, extending retention'
                ))

        return adjustments

    def calculate_agent_score(self, agent_name, days_back=30):
        """Calculate agent performance score"""
        recent_ratings = [
            r for r in self.metrics['user_ratings'][agent_name]
            if len(self.feedback['records']) > 0
        ]

        if not recent_ratings:
            return None

        avg_rating = statistics.mean(recent_ratings)
        consistency = 1.0 if len(set(recent_ratings)) <= 2 else 0.7

        return {
            'agent': agent_name,
            'avg_rating': avg_rating,
            'ratings_count': len(recent_ratings),
            'consistency': consistency,
            'overall_score': avg_rating * consistency
        }

    def generate_improvement_report(self):
        """Generate system improvement report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_health': {},
            'agent_scores': [],
            'adjustments_made': defaultdict(list),
            'recommendations': []
        }

        # Score each agent
        for agent_name in self.metrics['user_ratings'].keys():
            score = self.calculate_agent_score(agent_name)
            if score:
                report['agent_scores'].append(score)

        # Summarize adjustments
        for agent_name, improvements in self.metrics['improvements'].items():
            report['adjustments_made'][agent_name] = len(improvements)

        # Generate recommendations
        if report['agent_scores']:
            low_performers = [
                a['agent'] for a in report['agent_scores']
                if a['overall_score'] < 6.0
            ]
            if low_performers:
                report['recommendations'].append(
                    f"Focus on improving: {', '.join(low_performers)}"
                )

            high_performers = [
                a['agent'] for a in report['agent_scores']
                if a['overall_score'] >= 8.0
            ]
            if high_performers:
                report['recommendations'].append(
                    f"Leverage strengths of: {', '.join(high_performers)}"
                )

        return report

def main():
    print("=" * 70)
    print("SELF-IMPROVING AI SYSTEM")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    system = SelfImprovingSystem()

    print("System initialized")
    print(f"Current parameters: {system.parameters}\n")

    # Example: Simulate feedback
    print("=" * 70)
    print("FEEDBACK EXAMPLES")
    print("=" * 70)

    # Example 1: Good output
    print("\n1. User rates Performance Monitor (9/10)")
    system.submit_feedback(
        'performance_monitor',
        'report-001',
        9,
        'Great insights, very useful for strategy. Accurate metrics.'
    )

    # Example 2: Too strict
    print("2. User rates Pre-Publish Gate (3/10)")
    system.submit_feedback(
        'prepublish_gate',
        'gate-001',
        3,
        'Too strict on /stop-slop. Blocking quality content. Threshold too strict.'
    )

    # Example 3: Missing duplicates
    print("3. User rates Duplicate Detector (4/10)")
    system.submit_feedback(
        'duplicate_detector',
        'dupe-001',
        4,
        'Missed several duplicates. Similar content not caught.'
    )

    print("\n" + "=" * 70)
    print("IMPROVEMENT REPORT")
    print("=" * 70)

    report = system.generate_improvement_report()

    print(f"\nAgent scores:")
    for agent_score in report['agent_scores']:
        print(f"  {agent_score['agent']}: {agent_score['overall_score']:.1f}/10 ({agent_score['ratings_count']} ratings)")

    print(f"\nAdjustments made:")
    for agent, count in report['adjustments_made'].items():
        print(f"  {agent}: {count}")

    if report['recommendations']:
        print(f"\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

    print(f"\nUpdated parameters:")
    for param, value in system.parameters.items():
        print(f"  {param}: {value}")

    # Save report
    with open('improvement-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to improvement-report.json")
    print(f"✓ Parameters saved to agent-parameters.json")
    print(f"✓ Feedback log saved to agent-feedback.json")

if __name__ == '__main__':
    main()
