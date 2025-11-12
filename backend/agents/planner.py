# planner.py
import datetime
from icalendar import Calendar, Event

class PlannerAgent:
    def __init__(self, start_date=None):
        self.start_date = start_date or datetime.date.today()

    def create_revision_schedule(self, all_topics, accuracy_store):
        """
        Builds a smart revision schedule based on topic difficulty derived from quiz accuracy.
        """
        plan = []
        scheduled_topics = set()

        # Prioritize difficult topics
        for topic, scores in accuracy_store.items():
            if scores["incorrect"] > scores["correct"]:
                # High priority: Review soon
                revise_on = self.start_date + datetime.timedelta(days=1)
                plan.append({
                    "topic": topic,
                    "revise_on": str(revise_on),
                    "status": "difficult"
                })
                scheduled_topics.add(topic)
            elif scores["incorrect"] > 0:
                # Medium priority: Review in a few days
                revise_on = self.start_date + datetime.timedelta(days=3)
                plan.append({
                    "topic": topic,
                    "revise_on": str(revise_on),
                    "status": "needs practice"
                })
                scheduled_topics.add(topic)

        # Add remaining topics that are not yet in the plan
        day_offset = 3
        for topic in all_topics:
            if topic not in scheduled_topics:
                day_offset += 1
                revise_on = self.start_date + datetime.timedelta(days=day_offset)
                plan.append({
                    "topic": topic,
                    "revise_on": str(revise_on),
                    "status": "pending"
                })
        
        # Sort plan by date
        plan.sort(key=lambda x: x["revise_on"])
        return plan

    def to_ics(self, plan):
        """Converts a revision plan to an iCalendar (.ics) file format."""
        cal = Calendar()
        cal.add('prodid', '-//Study Agent//Smart Planner//EN')
        cal.add('version', '2.0')

        for item in plan:
            event = Event()
            event.add('summary', f"Review: {item['topic']}")
            
            # Convert date string to datetime object
            rev_date = datetime.datetime.strptime(item['revise_on'], '%Y-%m-%d').date()
            event.add('dtstart', rev_date)
            event.add('dtend', rev_date)
            event.add('dtstamp', datetime.datetime.now())
            event.add('description', f"Status: {item.get('status', 'pending')}")
            cal.add_component(event)

        return cal.to_ical()
