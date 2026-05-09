from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


RESULT_MARKER = "__LLD_RESULT__"
EXEC_TIMEOUT_SECONDS = 3


def block(text: str) -> str:
    return textwrap.dedent(text).strip("\n")


@dataclass(frozen=True)
class PatternCard:
    name: str
    family: str
    intent: str
    signals: str
    pitfall: str
    python_tip: str


@dataclass(frozen=True)
class Task:
    id: str
    kind: str
    prompt: str
    difficulty: str
    tags: tuple[str, ...] = ()
    options: tuple[str, ...] = ()
    answer_index: int | None = None
    explanation: str = ""
    starter: str = ""
    solution: str = ""
    hint: str = ""
    checklist: tuple[str, ...] = ()
    validator: str = ""


@dataclass(frozen=True)
class Lesson:
    id: str
    number: int
    title: str
    focus: tuple[str, ...]
    overview: str
    patterns: tuple[str, ...]
    badge: str
    tasks: tuple[Task, ...] = field(default_factory=tuple)


PATTERN_LIBRARY: dict[str, PatternCard] = {
    "Singleton": PatternCard(
        "Singleton",
        "Creational",
        "Guarantee one shared instance behind a narrow access point.",
        "Useful for process-wide coordination like config snapshots or in-memory registries.",
        "It quietly turns into global mutable state and makes testing harder.",
        "Prefer dependency injection or a module-level object unless you truly need lifecycle control.",
    ),
    "Factory Method": PatternCard(
        "Factory Method",
        "Creational",
        "Move conditional object creation behind one method or function.",
        "Use when callers need a channel, parser, or handler but should not know the concrete class.",
        "Do not hide a plain constructor behind a factory when nothing varies.",
        "In Python, a small mapping function is often enough.",
    ),
    "Abstract Factory": PatternCard(
        "Abstract Factory",
        "Creational",
        "Create families of related objects that must stay compatible.",
        "Strong fit for provider-specific suites like AWS/GCP, theme packs, or environment bundles.",
        "It gets ceremonial fast when there is only one real family.",
        "Keep the product family small and coherent.",
    ),
    "Builder": PatternCard(
        "Builder",
        "Creational",
        "Assemble a complex object through readable staged steps.",
        "Great for fluent APIs, staged validation, and interview questions with many optional parts.",
        "Do not wrap tiny value objects in a builder just to use the pattern name.",
        "Return self for chainable steps and validate clearly at build time.",
    ),
    "Prototype": PatternCard(
        "Prototype",
        "Creational",
        "Clone a configured object instead of rebuilding it from scratch.",
        "Useful for templates, simulation seeds, and mutable baseline objects.",
        "Shallow copies of nested mutable state are the classic trap.",
        "Be explicit about copy semantics.",
    ),
    "Adapter": PatternCard(
        "Adapter",
        "Structural",
        "Translate one interface into another that your domain expects.",
        "Use when a vendor SDK or legacy shape does not match your core model.",
        "If vendor terms still leak through the whole codebase, the adapter failed.",
        "Keep the wrapper thin and domain-focused.",
    ),
    "Bridge": PatternCard(
        "Bridge",
        "Structural",
        "Split an abstraction from the implementation axis so both can vary independently.",
        "Use when two dimensions evolve separately, like report type and render backend.",
        "It is easy to mistake Bridge for Strategy; Bridge models a durable split.",
        "Protocols or tiny interfaces keep the implementation side lightweight.",
    ),
    "Composite": PatternCard(
        "Composite",
        "Structural",
        "Treat leaves and containers uniformly in a tree structure.",
        "Great for menus, folders, permissions, org charts, and expression trees.",
        "Do not force Composite when the domain is really an arbitrary graph.",
        "Recursive dataclasses read well in Python.",
    ),
    "Decorator": PatternCard(
        "Decorator",
        "Structural",
        "Wrap an object to add responsibilities while preserving the same outward role.",
        "Useful for logging, retries, caching, metrics, and auth enrichment.",
        "If the wrapper must know too much internal state, cohesion is already slipping.",
        "Keep the wrapped method signature stable.",
    ),
    "Facade": PatternCard(
        "Facade",
        "Structural",
        "Expose one clean entry point over a messy subsystem.",
        "Strong fit for machine-coding workflows that coordinate several services.",
        "A facade should simplify collaboration, not become a god object.",
        "Think orchestrator, not dump-everything-here box.",
    ),
    "Flyweight": PatternCard(
        "Flyweight",
        "Structural",
        "Share intrinsic immutable state across many logical objects.",
        "Use when you have huge counts of similar objects with small varying context.",
        "Premature flyweights trade clarity for tiny savings.",
        "Separate shared state from per-instance context.",
    ),
    "Proxy": PatternCard(
        "Proxy",
        "Structural",
        "Stand in for another object to control access, loading, caching, or remoting.",
        "Useful for lazy loading, auth gates, caching remote calls, and expensive resources.",
        "If the wrapper changes semantics instead of controlling access, you may want Decorator.",
        "A proxy usually owns lifecycle and access policy.",
    ),
    "Strategy": PatternCard(
        "Strategy",
        "Behavioral",
        "Swap algorithms behind a stable interface.",
        "Perfect for pricing, ranking, assignment, retry, and routing policies.",
        "If behavior changes because lifecycle state changed, State is usually the better fit.",
        "Protocols keep strategy objects tiny and testable.",
    ),
    "Observer": PatternCard(
        "Observer",
        "Behavioral",
        "Broadcast change events to subscribers without hardwiring each consumer.",
        "Great for notifications, analytics, cache invalidation, and read-model updates.",
        "Unbounded fan-out and implicit ordering dependencies get messy quickly.",
        "Callables are often enough for subscribers in Python.",
    ),
    "Command": PatternCard(
        "Command",
        "Behavioral",
        "Wrap an action as an object so it can be queued, logged, retried, or undone.",
        "Useful for undo stacks, background work, and explicit action histories.",
        "If command objects only forward one line forever, the indirection is wasted.",
        "Dataclasses make command payloads easy to inspect.",
    ),
    "State": PatternCard(
        "State",
        "Behavioral",
        "Model behavior that changes with lifecycle state.",
        "Strong fit when transitions are explicit and legal operations vary by state.",
        "Do not replace a tiny boolean with a forest of classes for no gain.",
        "Enums plus state objects can coexist cleanly.",
    ),
    "Template Method": PatternCard(
        "Template Method",
        "Behavioral",
        "Keep the high-level workflow fixed while leaving some steps customizable.",
        "Useful when every pipeline follows the same broad sequence.",
        "Inheritance-heavy templates become brittle when many axes vary.",
        "Keep hooks narrow and the skeleton obvious.",
    ),
    "Iterator": PatternCard(
        "Iterator",
        "Behavioral",
        "Traverse a collection without exposing its internal storage details.",
        "Good for pages, streams, trees, and repository abstractions.",
        "Custom iterator classes are overkill when a generator solves the job.",
        "Generators are usually the Pythonic answer.",
    ),
    "Chain of Responsibility": PatternCard(
        "Chain of Responsibility",
        "Behavioral",
        "Pass a request through handlers until one handles it.",
        "Great for validation pipelines, escalation flows, and layered checks.",
        "Long implicit chains are hard to debug when ownership is unclear.",
        "Make fallthrough explicit and local.",
    ),
    "Mediator": PatternCard(
        "Mediator",
        "Behavioral",
        "Centralize collaboration so peers stop coordinating directly with each other.",
        "Useful when many objects would otherwise talk in a tangled dependency mesh.",
        "If every business rule accumulates there, the mediator turns into a god object.",
        "Keep peers simple and the mediator workflow-focused.",
    ),
    "Memento": PatternCard(
        "Memento",
        "Behavioral",
        "Capture and restore object state without exposing internals.",
        "Useful for undo, draft snapshots, and resumable workflows.",
        "Snapshotting giant mutable graphs repeatedly can be expensive and leaky.",
        "Immutable snapshots are easier to reason about.",
    ),
    "Interpreter": PatternCard(
        "Interpreter",
        "Behavioral",
        "Represent a tiny grammar as composable expression objects.",
        "Useful for interview-sized rules engines and mini DSLs.",
        "It falls apart when the language grows large or unbounded.",
        "Keep the grammar tiny and composable.",
    ),
    "Visitor": PatternCard(
        "Visitor",
        "Behavioral",
        "Add new operations across a stable structure without editing every element each time.",
        "Useful when node types are stable but analyses keep growing.",
        "If node types change frequently, Visitor becomes maintenance glue.",
        "Use it when operations change more often than the structure.",
    ),
}


def quiz(task_id: str, prompt: str, difficulty: str, tags: tuple[str, ...], options: tuple[str, ...], answer_index: int, explanation: str) -> Task:
    return Task(
        id=task_id,
        kind="quiz",
        prompt=prompt,
        difficulty=difficulty,
        tags=tags,
        options=options,
        answer_index=answer_index,
        explanation=explanation,
    )


def code_task(
    task_id: str,
    prompt: str,
    difficulty: str,
    tags: tuple[str, ...],
    starter: str,
    solution: str,
    hint: str,
    checklist: tuple[str, ...],
    validator: str,
) -> Task:
    return Task(
        id=task_id,
        kind="code",
        prompt=prompt,
        difficulty=difficulty,
        tags=tags,
        starter=block(starter),
        solution=block(solution),
        hint=hint,
        checklist=checklist,
        validator=block(validator),
    )


VALIDATION_PREAMBLE = block(
    f"""
    import json

    checks = []

    def expect(condition, success, failure=None):
        checks.append({{"ok": bool(condition), "message": success if condition else (failure or success)}})

    def expect_equal(actual, expected, label):
        if actual == expected:
            checks.append({{"ok": True, "message": label}})
        else:
            checks.append({{"ok": False, "message": f"{{label}}. Expected {{expected!r}}, got {{actual!r}}"}})

    def finish(summary):
        payload = {{
            "correct": all(item["ok"] for item in checks),
            "summary": summary,
            "checks": checks,
        }}
        print("{RESULT_MARKER}" + json.dumps(payload))
    """
)


def pitfall_task(prefix: str, pattern_name: str, difficulty: str, distractors: tuple[str, str, str]) -> Task:
    pattern = PATTERN_LIBRARY[pattern_name]
    options = (
        pattern.pitfall,
        PATTERN_LIBRARY[distractors[0]].pitfall,
        PATTERN_LIBRARY[distractors[1]].pitfall,
        PATTERN_LIBRARY[distractors[2]].pitfall,
    )
    return quiz(
        f"{prefix}-pitfall",
        f"What is the most important caution to keep in mind when you use {pattern_name} in an interview design?",
        difficulty,
        (pattern_name.lower().replace(" ", "-"), "pitfall"),
        options,
        0,
        f"For {pattern_name}, the sharpest warning is: {pattern.pitfall}",
    )


def solid_lesson() -> Lesson:
    return Lesson(
        id="solid-foundations",
        number=1,
        title="SOLID Foundations",
        focus=("responsibility slicing", "composition", "interfaces", "interview judgment"),
        overview="Before pattern names, get the change axes right. Clean interview LLD usually starts with smaller responsibilities, injected policies, and collaborators that are easy to test.",
        patterns=(),
        badge="Foundation",
        tasks=(
            quiz(
                "solid-q1",
                "A checkout service contains channel-specific branches for email, SMS, push, and WhatsApp inside one `send_receipt` method. New channels keep coming. What is the healthiest refactor?",
                "medium",
                ("solid", "dip", "ocp"),
                (
                    "Move the branches into a helper module and keep checkout in charge of selection.",
                    "Inject a sender interface or strategy so checkout depends on an abstraction instead of concrete channels.",
                    "Keep one large match-case so all branches remain explicit in one place.",
                    "Make checkout inherit from a sender base class and override per channel.",
                ),
                1,
                "The volatile part is channel behavior. Push that behind an abstraction and keep checkout focused on workflow.",
            ),
            quiz(
                "solid-q2",
                "A `ReportExporter` interface exposes `export_pdf`, `export_csv`, `export_xlsx`, and `export_html`, but some clients only need one method. What is the core design smell?",
                "medium",
                ("solid", "isp"),
                (
                    "Liskov Substitution is broken because interfaces should always have one method.",
                    "Interface Segregation is violated because clients depend on methods they do not need.",
                    "Single Responsibility is violated because exporters should never return bytes.",
                    "Factory Method should replace the interface entirely.",
                ),
                1,
                "This is Interface Segregation: split capabilities so clients depend only on what they actually use.",
            ),
            code_task(
                "solid-c1",
                "Implement `dispatch_invoices(invoices, sender)` so it delegates to the injected sender and preserves invoice order.",
                "medium",
                ("solid", "dip", "testability"),
                """
                from dataclasses import dataclass
                from typing import Protocol

                @dataclass(frozen=True)
                class Invoice:
                    id: str
                    amount: int
                    customer: str

                class Sender(Protocol):
                    def send(self, invoice: Invoice) -> str:
                        ...

                class EmailSender:
                    def send(self, invoice: Invoice) -> str:
                        return f"email:{invoice.customer}:{invoice.amount}"

                def dispatch_invoices(invoices, sender):
                    raise NotImplementedError
                """,
                """
                from dataclasses import dataclass
                from typing import Protocol

                @dataclass(frozen=True)
                class Invoice:
                    id: str
                    amount: int
                    customer: str

                class Sender(Protocol):
                    def send(self, invoice: Invoice) -> str:
                        ...

                class EmailSender:
                    def send(self, invoice: Invoice) -> str:
                        return f"email:{invoice.customer}:{invoice.amount}"

                def dispatch_invoices(invoices, sender):
                    return [sender.send(invoice) for invoice in invoices]
                """,
                "Do not branch on sender type. Just collaborate with the object you were given.",
                (
                    "No channel-specific conditionals inside dispatch_invoices.",
                    "Works with any object exposing send(invoice).",
                    "Preserves invoice order.",
                ),
                """
                Invoice = namespace.get("Invoice")
                EmailSender = namespace.get("EmailSender")
                dispatch = namespace.get("dispatch_invoices")
                expect(callable(dispatch), "dispatch_invoices is defined", "Define dispatch_invoices")
                if callable(dispatch) and Invoice and EmailSender:
                    invoices = [Invoice("i1", 100, "acme"), Invoice("i2", 200, "globex")]
                    expect_equal(dispatch(invoices, EmailSender()), ["email:acme:100", "email:globex:200"], "dispatch preserves order and delegates")
                finish("Nice. That is the shape of dependency inversion interviewers usually want.")
                """,
            ),
        ),
    )


def singleton_lesson() -> Lesson:
    return Lesson(
        id="singleton-pattern",
        number=2,
        title="Singleton Pattern",
        focus=("shared instance", "lifecycle control", "global state tradeoffs"),
        overview="Singleton is about one controlled instance, not about making things easy to access from everywhere.",
        patterns=("Singleton",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "singleton-q1",
                "A process should expose exactly one in-memory feature-flag registry shared by all callers in the same runtime. Which pattern fits most directly?",
                "easy",
                ("singleton", "creational"),
                ("Singleton", "Prototype", "Builder", "Decorator"),
                0,
                "The requirement is about exactly one shared runtime instance.",
            ),
            quiz(
                "singleton-q2",
                "Which statement best separates Singleton from plain global access?",
                "medium",
                ("singleton", "tradeoffs"),
                (
                    "Singleton is valuable because it removes the need for dependency injection everywhere.",
                    "Singleton controls instance creation and lifecycle; easy global access by itself is not the goal.",
                    "Singleton is the right answer whenever multiple classes read the same data.",
                    "Singleton should replace constructor injection in most interview designs.",
                ),
                1,
                "The pattern is about controlled creation and a single instance, not convenience globals.",
            ),
            code_task(
                "singleton-c1",
                "Implement `AppConfig.instance()` so it always returns the same `AppConfig` object.",
                "medium",
                ("singleton", "creational"),
                """
                class AppConfig:
                    _instance = None

                    def __init__(self):
                        self.values = {}

                    @classmethod
                    def instance(cls):
                        raise NotImplementedError
                """,
                """
                class AppConfig:
                    _instance = None

                    def __init__(self):
                        self.values = {}

                    @classmethod
                    def instance(cls):
                        if cls._instance is None:
                            cls._instance = cls()
                        return cls._instance
                """,
                "Create once, reuse afterward.",
                (
                    "Multiple calls return the same object.",
                    "State written through one reference is visible through another.",
                ),
                """
                AppConfig = namespace.get("AppConfig")
                expect(AppConfig is not None, "AppConfig exists", "Define AppConfig")
                if AppConfig is not None:
                    first = AppConfig.instance()
                    second = AppConfig.instance()
                    expect(first is second, "instance returns the same object", "instance should return one shared object")
                    first.values["mode"] = "prod"
                    expect_equal(second.values["mode"], "prod", "State is shared through the singleton instance")
                finish("Good. Just remember the interview follow-up: where can this hurt testing or coupling?")
                """,
            ),
        ),
    )


def factory_method_lesson() -> Lesson:
    return Lesson(
        id="factory-method-pattern",
        number=3,
        title="Factory Method Pattern",
        focus=("conditional creation", "construction isolation", "call-site simplicity"),
        overview="Factory Method is the pattern you reach for when callers should ask for a capability but stay ignorant of the concrete class selection rules.",
        patterns=("Factory Method",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "factory-q1",
                "A router must choose `EmailSender`, `SmsSender`, or `SlackSender` based on a channel string, but the caller should only ask for a sender. Which pattern fits best?",
                "easy",
                ("factory-method", "creational"),
                ("Factory Method", "Adapter", "Prototype", "Visitor"),
                0,
                "This is straightforward conditional construction hidden from the caller.",
            ),
            quiz(
                "factory-q2",
                "When is Factory Method probably overkill?",
                "medium",
                ("factory-method", "tradeoffs"),
                (
                    "When there is no meaningful variation and a direct constructor call is already clear.",
                    "When object creation depends on one runtime input.",
                    "When callers should not know concrete classes.",
                    "When multiple concrete implementations exist.",
                ),
                0,
                "If nothing actually varies, a factory only adds ceremony.",
            ),
            code_task(
                "factory-c1",
                "Implement `NotificationFactory.build(channel)` for `email`, `slack`, and `sms`.",
                "medium",
                ("factory-method", "creational"),
                """
                class EmailSender:
                    def send(self, user, message):
                        return f"email:{user}:{message}"

                class SlackSender:
                    def send(self, user, message):
                        return f"slack:{user}:{message}"

                class SmsSender:
                    def send(self, user, message):
                        return f"sms:{user}:{message}"

                class NotificationFactory:
                    def build(self, channel):
                        raise NotImplementedError
                """,
                """
                class EmailSender:
                    def send(self, user, message):
                        return f"email:{user}:{message}"

                class SlackSender:
                    def send(self, user, message):
                        return f"slack:{user}:{message}"

                class SmsSender:
                    def send(self, user, message):
                        return f"sms:{user}:{message}"

                class NotificationFactory:
                    def build(self, channel):
                        mapping = {
                            "email": EmailSender,
                            "slack": SlackSender,
                            "sms": SmsSender,
                        }
                        if channel not in mapping:
                            raise ValueError(f"Unsupported channel: {channel}")
                        return mapping[channel]()
                """,
                "A tiny mapping is enough here.",
                (
                    "Returns the right sender type.",
                    "Unsupported channels fail loudly.",
                ),
                """
                NotificationFactory = namespace.get("NotificationFactory")
                expect(NotificationFactory is not None, "NotificationFactory exists", "Define NotificationFactory")
                if NotificationFactory is not None:
                    factory = NotificationFactory()
                    expect_equal(factory.build("email").send("ana", "hi"), "email:ana:hi", "email sender works")
                    expect_equal(factory.build("slack").send("ana", "hi"), "slack:ana:hi", "slack sender works")
                    expect_equal(factory.build("sms").send("ana", "hi"), "sms:ana:hi", "sms sender works")
                    try:
                        factory.build("pagerduty")
                    except ValueError:
                        checks.append({"ok": True, "message": "Unsupported channels raise ValueError"})
                    else:
                        checks.append({"ok": False, "message": "Unsupported channels should raise ValueError"})
                finish("Nice. One clean construction point is the whole win here.")
                """,
            ),
        ),
    )


def abstract_factory_lesson() -> Lesson:
    return Lesson(
        id="abstract-factory-pattern",
        number=4,
        title="Abstract Factory Pattern",
        focus=("object families", "provider consistency", "suite construction"),
        overview="Abstract Factory matters when several created objects must come from the same family and remain compatible.",
        patterns=("Abstract Factory",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "abstract-factory-q1",
                "A deployment tool must create a VM, load balancer, and metrics client together for either AWS or GCP, and the family must stay internally compatible. Which pattern fits best?",
                "medium",
                ("abstract-factory", "creational"),
                ("Abstract Factory", "Factory Method", "Bridge", "Decorator"),
                0,
                "The key phrase is 'related family of objects that must stay compatible'.",
            ),
            quiz(
                "abstract-factory-q2",
                "What is the strongest signal that you need Abstract Factory rather than Factory Method?",
                "medium",
                ("abstract-factory", "comparison"),
                (
                    "Only one object needs construction, but you want cleaner code.",
                    "Several related objects must vary together as one provider-specific suite.",
                    "You want to add logging around an existing object.",
                    "You want to translate one API shape into another.",
                ),
                1,
                "Factory Method handles one construction point; Abstract Factory coordinates a family.",
            ),
            pitfall_task("abstract-factory", "Abstract Factory", "hard", ("Singleton", "Proxy", "Observer")),
        ),
    )


def builder_lesson() -> Lesson:
    return Lesson(
        id="builder-pattern",
        number=5,
        title="Builder Pattern",
        focus=("fluent construction", "staged validation", "readable setup"),
        overview="Builder is for construction that benefits from staging and readability, not for inflating trivial constructors.",
        patterns=("Builder",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "builder-q1",
                "You need a readable API to assemble a query with optional filters, grouping, ordering, and limits. Which pattern makes the call site cleanest?",
                "easy",
                ("builder", "api-design"),
                ("Builder", "Prototype", "Visitor", "Adapter"),
                0,
                "This is classic Builder territory: lots of optional pieces and a desire for readable chaining.",
            ),
            quiz(
                "builder-q2",
                "What is the main design advantage of Builder over a giant constructor here?",
                "medium",
                ("builder", "tradeoffs"),
                (
                    "It guarantees there will only ever be one instance.",
                    "It lets callers express optional construction steps readably and validates at the end.",
                    "It removes the need for domain objects.",
                    "It automatically makes the object immutable.",
                ),
                1,
                "Builder improves readability and staged validation, not magical immutability or uniqueness.",
            ),
            code_task(
                "builder-c1",
                "Implement a tiny `QueryBuilder` supporting `select`, `from_`, `where`, `order_by`, and `build`.",
                "hard",
                ("builder", "fluent-api"),
                """
                class QueryBuilder:
                    def __init__(self):
                        self._columns = []
                        self._table = ""
                        self._filters = []
                        self._order = ""

                    def select(self, *columns):
                        raise NotImplementedError

                    def from_(self, table):
                        raise NotImplementedError

                    def where(self, condition):
                        raise NotImplementedError

                    def order_by(self, clause):
                        raise NotImplementedError

                    def build(self):
                        raise NotImplementedError
                """,
                """
                class QueryBuilder:
                    def __init__(self):
                        self._columns = []
                        self._table = ""
                        self._filters = []
                        self._order = ""

                    def select(self, *columns):
                        self._columns = list(columns)
                        return self

                    def from_(self, table):
                        self._table = table
                        return self

                    def where(self, condition):
                        self._filters.append(condition)
                        return self

                    def order_by(self, clause):
                        self._order = clause
                        return self

                    def build(self):
                        if not self._columns or not self._table:
                            raise ValueError("select and from_ are required")
                        sql = f"SELECT {', '.join(self._columns)} FROM {self._table}"
                        if self._filters:
                            sql += " WHERE " + " AND ".join(self._filters)
                        if self._order:
                            sql += f" ORDER BY {self._order}"
                        return sql
                """,
                "Return `self` from the staged methods.",
                (
                    "Method chaining works.",
                    "Multiple where clauses join with AND.",
                    "Missing required pieces fail clearly.",
                ),
                """
                QueryBuilder = namespace.get("QueryBuilder")
                expect(QueryBuilder is not None, "QueryBuilder exists", "Define QueryBuilder")
                if QueryBuilder is not None:
                    sql = QueryBuilder().select("id", "name").from_("users").where("active = 1").where("score > 80").order_by("score DESC").build()
                    expect_equal(sql, "SELECT id, name FROM users WHERE active = 1 AND score > 80 ORDER BY score DESC", "Builder assembles SQL correctly")
                finish("Good. Builder should make the call site nicer than the alternative.")
                """,
            ),
        ),
    )


def prototype_lesson() -> Lesson:
    return Lesson(
        id="prototype-pattern",
        number=6,
        title="Prototype Pattern",
        focus=("cloning", "copy semantics", "baseline templates"),
        overview="Prototype is useful when the cheapest way to make a new object is to copy a configured existing one.",
        patterns=("Prototype",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "prototype-q1",
                "A team keeps one preconfigured interview simulation object and clones it per candidate before tweaking deadlines and question sets. Which pattern is the most direct fit?",
                "easy",
                ("prototype", "copying"),
                ("Prototype", "Builder", "Mediator", "Chain of Responsibility"),
                0,
                "Cloning a configured baseline is the center of gravity here.",
            ),
            quiz(
                "prototype-q2",
                "What is the most important implementation follow-up after choosing Prototype?",
                "medium",
                ("prototype", "copying", "mutability"),
                (
                    "Whether the copy should be shallow or deep for nested mutable state.",
                    "Whether the object should also be a singleton.",
                    "Whether all methods should become chainable.",
                    "Whether the object family should switch to Abstract Factory.",
                ),
                0,
                "The hard part is almost always copy semantics.",
            ),
            pitfall_task("prototype", "Prototype", "hard", ("Builder", "Strategy", "Observer")),
        ),
    )


def adapter_lesson() -> Lesson:
    return Lesson(
        id="adapter-pattern",
        number=7,
        title="Adapter Pattern",
        focus=("shape translation", "vendor integration", "domain-friendly interfaces"),
        overview="Adapter is for interface mismatch. Your domain should keep speaking its own language even when a dependency does not.",
        patterns=("Adapter",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "adapter-q1",
                "A payment SDK exposes `charge(amount_paise, account_ref)` while your domain wants `pay(amount_rupees, customer_id)`. Which pattern is the direct fit?",
                "easy",
                ("adapter", "integration"),
                ("Adapter", "Facade", "Decorator", "Bridge"),
                0,
                "That is an interface translation problem, which is exactly what Adapter solves.",
            ),
            quiz(
                "adapter-q2",
                "What is the strongest smell that an Adapter is poorly done?",
                "medium",
                ("adapter", "tradeoffs"),
                (
                    "The wrapper internally delegates to the SDK.",
                    "Vendor-specific terms keep leaking into the rest of the domain model and service APIs.",
                    "The adapter class has only one public method.",
                    "The adapter is smaller than the original SDK.",
                ),
                1,
                "If the whole codebase still speaks in vendor language, the translation layer did not do its job.",
            ),
            code_task(
                "adapter-c1",
                "Implement `PaymentsGatewayAdapter.pay(amount_rupees, customer_id)` over a paise-based SDK.",
                "medium",
                ("adapter", "integration"),
                """
                class LegacyPayments:
                    def charge(self, amount_paise, account_ref):
                        return f"legacy:{account_ref}:{amount_paise}"

                class PaymentsGatewayAdapter:
                    def __init__(self, legacy):
                        self.legacy = legacy

                    def pay(self, amount_rupees, customer_id):
                        raise NotImplementedError
                """,
                """
                class LegacyPayments:
                    def charge(self, amount_paise, account_ref):
                        return f"legacy:{account_ref}:{amount_paise}"

                class PaymentsGatewayAdapter:
                    def __init__(self, legacy):
                        self.legacy = legacy

                    def pay(self, amount_rupees, customer_id):
                        return self.legacy.charge(int(round(amount_rupees * 100)), customer_id)
                """,
                "The adapter owns the unit conversion.",
                (
                    "Converts rupees to paise.",
                    "Delegates with the customer id as account ref.",
                ),
                """
                Adapter = namespace.get("PaymentsGatewayAdapter")
                Legacy = namespace.get("LegacyPayments")
                expect(Adapter is not None and Legacy is not None, "Adapter classes exist", "Keep the adapter classes defined")
                if Adapter and Legacy:
                    adapter = Adapter(Legacy())
                    expect_equal(adapter.pay(199.5, "cust-7"), "legacy:cust-7:19950", "Adapter converts and delegates correctly")
                finish("Nice. A good adapter shrinks external weirdness down to one seam.")
                """,
            ),
        ),
    )


def bridge_lesson() -> Lesson:
    return Lesson(
        id="bridge-pattern",
        number=8,
        title="Bridge Pattern",
        focus=("two axes of variation", "abstraction split", "independent evolution"),
        overview="Bridge is what you use when two dimensions should evolve independently and neither one should own the other.",
        patterns=("Bridge",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "bridge-q1",
                "A document service has report types like invoice and scorecard, while rendering backends like HTML and PDF also evolve independently. Which pattern is strongest here?",
                "medium",
                ("bridge", "structure"),
                ("Bridge", "Strategy", "Prototype", "Composite"),
                0,
                "This is the canonical 'two durable axes of variation' signal for Bridge.",
            ),
            quiz(
                "bridge-q2",
                "Which distinction is most accurate?",
                "hard",
                ("bridge", "comparison"),
                (
                    "Bridge is for one swappable algorithm; Strategy is for two stable variation dimensions.",
                    "Bridge splits abstraction from implementation for long-lived independent variation; Strategy swaps one algorithm behind a stable interface.",
                    "Bridge and Adapter are interchangeable if a wrapper is involved.",
                    "Bridge is mainly about object creation.",
                ),
                1,
                "Strategy swaps one policy. Bridge models two long-lived axes.",
            ),
            pitfall_task("bridge", "Bridge", "hard", ("Strategy", "Decorator", "Singleton")),
        ),
    )


def composite_lesson() -> Lesson:
    return Lesson(
        id="composite-pattern",
        number=9,
        title="Composite Pattern",
        focus=("trees", "uniform treatment", "recursive structure"),
        overview="Composite helps when leaves and containers should answer the same questions through one shared interface.",
        patterns=("Composite",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "composite-q1",
                "You need folders and files to both answer `size()` so callers can work uniformly over a tree. Which pattern fits best?",
                "easy",
                ("composite", "trees"),
                ("Composite", "Decorator", "Visitor", "Chain of Responsibility"),
                0,
                "This is a classic uniform-leaf-and-container tree problem.",
            ),
            quiz(
                "composite-q2",
                "When should you avoid Composite?",
                "medium",
                ("composite", "tradeoffs"),
                (
                    "When the domain is really a general graph with cross-links instead of a clean tree.",
                    "When recursion is available in Python.",
                    "When leaves and containers share some methods.",
                    "When a folder can contain files.",
                ),
                0,
                "Composite wants a tree-like ownership structure. Arbitrary graph logic changes the game.",
            ),
            code_task(
                "composite-c1",
                "Implement `FileNode.total_size()` and `FolderNode.total_size()` so folders sum nested children recursively.",
                "medium",
                ("composite", "recursion"),
                """
                class FileNode:
                    def __init__(self, size):
                        self.size = size

                    def total_size(self):
                        raise NotImplementedError

                class FolderNode:
                    def __init__(self, children):
                        self.children = list(children)

                    def total_size(self):
                        raise NotImplementedError
                """,
                """
                class FileNode:
                    def __init__(self, size):
                        self.size = size

                    def total_size(self):
                        return self.size

                class FolderNode:
                    def __init__(self, children):
                        self.children = list(children)

                    def total_size(self):
                        return sum(child.total_size() for child in self.children)
                """,
                "Leaves answer directly; containers recurse through children.",
                (
                    "File nodes return their own size.",
                    "Folder nodes sum nested totals recursively.",
                ),
                """
                FileNode = namespace.get("FileNode")
                FolderNode = namespace.get("FolderNode")
                expect(FileNode is not None and FolderNode is not None, "Composite classes exist", "Define FileNode and FolderNode")
                if FileNode and FolderNode:
                    tree = FolderNode([FileNode(3), FolderNode([FileNode(5), FileNode(2)])])
                    expect_equal(tree.total_size(), 10, "Folder totals recurse through nested children")
                finish("Good. Composite should make leaves and containers feel uniform to callers.")
                """,
            ),
        ),
    )


def decorator_lesson() -> Lesson:
    return Lesson(
        id="decorator-pattern",
        number=10,
        title="Decorator Pattern",
        focus=("wrapping behavior", "transparent enrichment", "layered responsibilities"),
        overview="Decorator is a clean way to add behavior around an existing collaborator while keeping the same outward role.",
        patterns=("Decorator",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "decorator-q1",
                "You want to add logging and retry behavior around an existing notifier without changing the notifier's public role. Which pattern fits best?",
                "easy",
                ("decorator", "wrapping"),
                ("Decorator", "Adapter", "Proxy", "Facade"),
                0,
                "You are layering extra behavior around the same outward interface.",
            ),
            quiz(
                "decorator-q2",
                "Which distinction is most helpful in interviews?",
                "medium",
                ("decorator", "comparison"),
                (
                    "Decorator mainly translates one interface into another.",
                    "Decorator adds responsibilities while keeping the same role; Adapter translates interfaces.",
                    "Decorator exists only for caching.",
                    "Decorator is the same thing as Proxy if a wrapper class is present.",
                ),
                1,
                "Decorator preserves the role and adds behavior. Adapter translates shape.",
            ),
            code_task(
                "decorator-c1",
                "Implement `LoggingNotifier.send(message)` so it calls the wrapped notifier and prepends `log:` to the returned value.",
                "medium",
                ("decorator", "wrapping"),
                """
                class BaseNotifier:
                    def send(self, message):
                        return f"sent:{message}"

                class LoggingNotifier:
                    def __init__(self, wrapped):
                        self.wrapped = wrapped

                    def send(self, message):
                        raise NotImplementedError
                """,
                """
                class BaseNotifier:
                    def send(self, message):
                        return f"sent:{message}"

                class LoggingNotifier:
                    def __init__(self, wrapped):
                        self.wrapped = wrapped

                    def send(self, message):
                        return f"log:{self.wrapped.send(message)}"
                """,
                "Keep the same outward method, add behavior around the wrapped call.",
                (
                    "Delegates to the wrapped notifier.",
                    "Adds behavior without changing the method role.",
                ),
                """
                BaseNotifier = namespace.get("BaseNotifier")
                LoggingNotifier = namespace.get("LoggingNotifier")
                expect(BaseNotifier is not None and LoggingNotifier is not None, "Decorator classes exist", "Define BaseNotifier and LoggingNotifier")
                if BaseNotifier and LoggingNotifier:
                    notifier = LoggingNotifier(BaseNotifier())
                    expect_equal(notifier.send("hi"), "log:sent:hi", "Decorator wraps the base notifier response")
                finish("Nice. That is the essence of Decorator in interview code.")
                """,
            ),
        ),
    )


def facade_lesson() -> Lesson:
    return Lesson(
        id="facade-pattern",
        number=11,
        title="Facade Pattern",
        focus=("subsystem simplification", "workflow entry point", "orchestration"),
        overview="Facade gives callers one clean entry point over a subsystem that would otherwise require too much coordination knowledge.",
        patterns=("Facade",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "facade-q1",
                "A support platform coordinates ticketing, notifications, and audit logging, but callers should open an incident through one simple method. Which pattern fits best?",
                "easy",
                ("facade", "workflow"),
                ("Facade", "Adapter", "Chain of Responsibility", "Visitor"),
                0,
                "This is subsystem simplification through one orchestrating front door.",
            ),
            quiz(
                "facade-q2",
                "What is the biggest design warning with Facade?",
                "medium",
                ("facade", "tradeoffs"),
                (
                    "It should expose every internal collaborator method directly to stay complete.",
                    "It can slowly become a god object if every workflow and rule is dumped into it.",
                    "It only works when there are exactly three collaborators.",
                    "It should always replace domain services.",
                ),
                1,
                "A facade should simplify access, not swallow the whole domain.",
            ),
            code_task(
                "facade-c1",
                "Implement `SupportPlatformFacade.open_incident(...)` so it coordinates ticketing, notifications, and audit logging.",
                "medium",
                ("facade", "workflow"),
                """
                class TicketingService:
                    def create(self, title, severity):
                        return {"ticket_id": f"T-{severity[:1].upper()}-{len(title)}", "title": title, "severity": severity}

                class NotificationService:
                    def notify(self, channel, message):
                        return f"{channel}:{message}"

                class AuditLog:
                    def write(self, event):
                        return f"audit:{event}"

                class SupportPlatformFacade:
                    def __init__(self, ticketing, notifier, audit):
                        self.ticketing = ticketing
                        self.notifier = notifier
                        self.audit = audit

                    def open_incident(self, title, severity, channel):
                        raise NotImplementedError
                """,
                """
                class TicketingService:
                    def create(self, title, severity):
                        return {"ticket_id": f"T-{severity[:1].upper()}-{len(title)}", "title": title, "severity": severity}

                class NotificationService:
                    def notify(self, channel, message):
                        return f"{channel}:{message}"

                class AuditLog:
                    def write(self, event):
                        return f"audit:{event}"

                class SupportPlatformFacade:
                    def __init__(self, ticketing, notifier, audit):
                        self.ticketing = ticketing
                        self.notifier = notifier
                        self.audit = audit

                    def open_incident(self, title, severity, channel):
                        ticket = self.ticketing.create(title, severity)
                        notification = self.notifier.notify(channel, f"{ticket['ticket_id']}:{title}")
                        audit = self.audit.write(f"opened:{ticket['ticket_id']}:{severity}")
                        return {"ticket": ticket, "notification": notification, "audit": audit}
                """,
                "Think orchestrator, not giant business-logic bucket.",
                (
                    "Delegates ticket creation.",
                    "Creates notification and audit entries from the same workflow.",
                ),
                """
                Facade = namespace.get("SupportPlatformFacade")
                TicketingService = namespace.get("TicketingService")
                NotificationService = namespace.get("NotificationService")
                AuditLog = namespace.get("AuditLog")
                expect(all(item is not None for item in (Facade, TicketingService, NotificationService, AuditLog)), "Facade classes exist", "Keep the facade classes defined")
                if all(item is not None for item in (Facade, TicketingService, NotificationService, AuditLog)):
                    facade = Facade(TicketingService(), NotificationService(), AuditLog())
                    result = facade.open_incident("api down", "high", "slack")
                    expect_equal(result["notification"], "slack:T-H-8:api down", "Facade orchestrates notification")
                    expect_equal(result["audit"], "audit:opened:T-H-8:high", "Facade orchestrates audit logging")
                finish("Good. The caller gets one simple method while the collaborators stay separate.")
                """,
            ),
        ),
    )


def flyweight_lesson() -> Lesson:
    return Lesson(
        id="flyweight-pattern",
        number=12,
        title="Flyweight Pattern",
        focus=("memory sharing", "intrinsic vs extrinsic state", "scale tradeoffs"),
        overview="Flyweight only earns its complexity when huge object counts make shared intrinsic state materially valuable.",
        patterns=("Flyweight",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "flyweight-q1",
                "A text editor has millions of characters but only a small set of shared font-style combinations. Which pattern helps share style objects efficiently?",
                "medium",
                ("flyweight", "memory"),
                ("Flyweight", "Prototype", "Decorator", "Singleton"),
                0,
                "This is about shared intrinsic state across huge numbers of logical objects.",
            ),
            quiz(
                "flyweight-q2",
                "Which statement captures the core idea of Flyweight?",
                "medium",
                ("flyweight", "concept"),
                (
                    "Every object should be immutable.",
                    "Shared intrinsic state lives in flyweights; changing context is supplied externally.",
                    "One process should own exactly one instance.",
                    "Object creation should be hidden behind a method.",
                ),
                1,
                "Flyweight separates shared state from per-instance context.",
            ),
            pitfall_task("flyweight", "Flyweight", "hard", ("Singleton", "Observer", "Template Method")),
        ),
    )


def proxy_lesson() -> Lesson:
    return Lesson(
        id="proxy-pattern",
        number=13,
        title="Proxy Pattern",
        focus=("access control", "lazy loading", "cached indirection"),
        overview="Proxy stands in for something else so it can control access, timing, or cost before the real object is touched.",
        patterns=("Proxy",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "proxy-q1",
                "A dashboard should lazy-load an expensive candidate report only when opened and reuse the result afterward. Which pattern is the direct fit?",
                "medium",
                ("proxy", "lazy-loading"),
                ("Proxy", "Decorator", "Facade", "Flyweight"),
                0,
                "This is access and loading control around an expensive target.",
            ),
            quiz(
                "proxy-q2",
                "What is the cleanest difference between Proxy and Decorator in interviews?",
                "medium",
                ("proxy", "comparison"),
                (
                    "Proxy controls access, loading, or indirection to a target; Decorator layers extra responsibilities around the same role.",
                    "Proxy and Decorator are the same whenever both use wrapper objects.",
                    "Decorator is for remote calls, Proxy is for logging.",
                    "Proxy mainly translates interface shapes while Decorator preserves them.",
                ),
                0,
                "Both wrap, but the reason for wrapping differs.",
            ),
            code_task(
                "proxy-c1",
                "Implement `LazyReportProxy.get()` so the expensive loader runs only once and later calls reuse the cached value.",
                "medium",
                ("proxy", "lazy-loading"),
                """
                class LazyReportProxy:
                    def __init__(self, loader):
                        self.loader = loader
                        self._cached = None

                    def get(self):
                        raise NotImplementedError
                """,
                """
                class LazyReportProxy:
                    def __init__(self, loader):
                        self.loader = loader
                        self._cached = None

                    def get(self):
                        if self._cached is None:
                            self._cached = self.loader()
                        return self._cached
                """,
                "The proxy controls when the expensive target is realized.",
                (
                    "Loader runs once on first access.",
                    "Later accesses reuse cached state.",
                ),
                """
                LazyReportProxy = namespace.get("LazyReportProxy")
                expect(LazyReportProxy is not None, "LazyReportProxy exists", "Define LazyReportProxy")
                if LazyReportProxy is not None:
                    calls = {"count": 0}
                    def loader():
                        calls["count"] += 1
                        return {"report": "ok"}
                    proxy = LazyReportProxy(loader)
                    expect_equal(proxy.get(), {"report": "ok"}, "First access loads the report")
                    expect_equal(proxy.get(), {"report": "ok"}, "Second access returns the cached report")
                    expect_equal(calls["count"], 1, "Loader runs only once")
                finish("Nice. Proxy is about controlling access to the real thing.")
                """,
            ),
        ),
    )


def strategy_lesson() -> Lesson:
    return Lesson(
        id="strategy-pattern",
        number=14,
        title="Strategy Pattern",
        focus=("policy swapping", "algorithm variation", "runtime behavior"),
        overview="Strategy is the pattern you use when one stable context should delegate to one of several interchangeable policies.",
        patterns=("Strategy",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "strategy-q1",
                "A delivery app computes fees differently for regular, surge, and premium contexts, but checkout itself should stay simple. Which pattern fits best?",
                "easy",
                ("strategy", "pricing"),
                ("Strategy", "State", "Bridge", "Mediator"),
                0,
                "This is a textbook swappable-policy problem.",
            ),
            quiz(
                "strategy-q2",
                "When is State usually a better fit than Strategy?",
                "medium",
                ("strategy", "state", "comparison"),
                (
                    "When callers should freely swap algorithms at runtime based on a policy choice.",
                    "When behavior changes because the object's lifecycle state changed and legal transitions matter.",
                    "When several related objects must be created together.",
                    "When a vendor API needs translation.",
                ),
                1,
                "Strategy is a policy choice. State is behavior coupled to lifecycle and transitions.",
            ),
            code_task(
                "strategy-c1",
                "Implement three pricing strategies and keep `Checkout.total(base_amount)` delegated to the injected policy.",
                "medium",
                ("strategy", "policies"),
                """
                class RegularPricing:
                    def total(self, base_amount):
                        raise NotImplementedError

                class SurgePricing:
                    def __init__(self, multiplier):
                        self.multiplier = multiplier

                    def total(self, base_amount):
                        raise NotImplementedError

                class PremiumPricing:
                    def total(self, base_amount):
                        raise NotImplementedError

                class Checkout:
                    def __init__(self, pricing):
                        self.pricing = pricing

                    def total(self, base_amount):
                        return self.pricing.total(base_amount)
                """,
                """
                class RegularPricing:
                    def total(self, base_amount):
                        return base_amount

                class SurgePricing:
                    def __init__(self, multiplier):
                        self.multiplier = multiplier

                    def total(self, base_amount):
                        return round(base_amount * self.multiplier, 2)

                class PremiumPricing:
                    def total(self, base_amount):
                        return round(base_amount * 0.9, 2)

                class Checkout:
                    def __init__(self, pricing):
                        self.pricing = pricing

                    def total(self, base_amount):
                        return self.pricing.total(base_amount)
                """,
                "Keep checkout boring. Put the algorithm in the strategy.",
                (
                    "Regular pricing returns the base amount.",
                    "Surge pricing multiplies the base amount.",
                    "Premium pricing applies a 10% discount.",
                ),
                """
                Checkout = namespace.get("Checkout")
                RegularPricing = namespace.get("RegularPricing")
                SurgePricing = namespace.get("SurgePricing")
                PremiumPricing = namespace.get("PremiumPricing")
                expect(all(item is not None for item in (Checkout, RegularPricing, SurgePricing, PremiumPricing)), "Strategy classes exist", "Keep the strategy classes defined")
                if all(item is not None for item in (Checkout, RegularPricing, SurgePricing, PremiumPricing)):
                    expect_equal(Checkout(RegularPricing()).total(100), 100, "Regular pricing works")
                    expect_equal(Checkout(SurgePricing(1.75)).total(120), 210.0, "Surge pricing works")
                    expect_equal(Checkout(PremiumPricing()).total(200), 180.0, "Premium pricing works")
                finish("Good. Strategy is strongest when the context stops caring which algorithm it got.")
                """,
            ),
        ),
    )


def observer_lesson() -> Lesson:
    return Lesson(
        id="observer-pattern",
        number=15,
        title="Observer Pattern",
        focus=("event fan-out", "publish-subscribe", "decoupled reactions"),
        overview="Observer is your baseline pattern for one-to-many event fan-out when the publisher should not know its consumers in detail.",
        patterns=("Observer",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "observer-q1",
                "An inventory service should publish stock changes to notifications, analytics, and cache invalidation without hard-coding those consumers. Which pattern fits best?",
                "easy",
                ("observer", "events"),
                ("Observer", "Mediator", "Visitor", "Builder"),
                0,
                "This is exactly what Observer is for: one publisher, many decoupled listeners.",
            ),
            quiz(
                "observer-q2",
                "When is Mediator a better fit than Observer?",
                "medium",
                ("observer", "mediator", "comparison"),
                (
                    "When several peers need a central coordinator to own workflow decisions rather than simple one-way event fan-out.",
                    "When listeners should react independently after one source changes.",
                    "When analytics and notifications both need the same event.",
                    "When event subscribers should stay decoupled from the publisher.",
                ),
                0,
                "Observer is fan-out. Mediator is workflow coordination among many peers.",
            ),
            code_task(
                "observer-c1",
                "Implement `InventorySubject.subscribe(listener)` and `restock(sku, quantity)` so listeners receive events in subscription order.",
                "medium",
                ("observer", "events"),
                """
                class InventorySubject:
                    def __init__(self):
                        self._listeners = []

                    def subscribe(self, listener):
                        raise NotImplementedError

                    def restock(self, sku, quantity):
                        raise NotImplementedError
                """,
                """
                class InventorySubject:
                    def __init__(self):
                        self._listeners = []

                    def subscribe(self, listener):
                        self._listeners.append(listener)

                    def restock(self, sku, quantity):
                        for listener in self._listeners:
                            listener(sku, quantity)
                """,
                "Just keep a listener list and notify in order.",
                (
                    "subscribe registers listeners.",
                    "restock fans out to every listener in a deterministic order.",
                ),
                """
                InventorySubject = namespace.get("InventorySubject")
                expect(InventorySubject is not None, "InventorySubject exists", "Define InventorySubject")
                if InventorySubject is not None:
                    subject = InventorySubject()
                    seen = []
                    subject.subscribe(lambda sku, qty: seen.append(("analytics", sku, qty)))
                    subject.subscribe(lambda sku, qty: seen.append(("notify", sku, qty)))
                    subject.restock("KB-1", 5)
                    expect_equal(seen, [("analytics", "KB-1", 5), ("notify", "KB-1", 5)], "Listeners receive events in subscription order")
                finish("Nice. That is a clean observer baseline you can later extend with retries or filtering.")
                """,
            ),
        ),
    )


def command_lesson() -> Lesson:
    return Lesson(
        id="command-pattern",
        number=16,
        title="Command Pattern",
        focus=("action objects", "undo", "queues", "auditability"),
        overview="Command shines when you want actions to be explicit objects that can be queued, retried, logged, undone, or replayed.",
        patterns=("Command",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "command-q1",
                "Why is `CreateOrderCommand` often stronger than a plain service call in an interview design?",
                "medium",
                ("command", "actions"),
                (
                    "Because every object-oriented solution should wrap methods in objects.",
                    "Because action intent becomes explicit, making queuing, retry, logging, and undo easier.",
                    "Because command objects remove the need for services.",
                    "Because CQRS requires it.",
                ),
                1,
                "Command pays off when actions need a lifecycle beyond one immediate method call.",
            ),
            quiz(
                "command-q2",
                "Which scenario most strongly points to Command?",
                "medium",
                ("command", "selection"),
                (
                    "A parser must translate SDK method names into domain names.",
                    "A toolbar needs undoable actions like bold, italic, and insert image.",
                    "A notifier needs logging around send.",
                    "A repository exposes a paginated iterator.",
                ),
                1,
                "Undoable toolbar actions are a classic Command scenario.",
            ),
            code_task(
                "command-c1",
                "Implement `TurnOnCommand.execute()` so the command delegates to the light.",
                "easy",
                ("command", "actions"),
                """
                class Light:
                    def turn_on(self):
                        return "light:on"

                class TurnOnCommand:
                    def __init__(self, light):
                        self.light = light

                    def execute(self):
                        raise NotImplementedError
                """,
                """
                class Light:
                    def turn_on(self):
                        return "light:on"

                class TurnOnCommand:
                    def __init__(self, light):
                        self.light = light

                    def execute(self):
                        return self.light.turn_on()
                """,
                "A command packages an action and delegates execution.",
                (
                    "execute delegates to the receiver.",
                ),
                """
                Light = namespace.get("Light")
                TurnOnCommand = namespace.get("TurnOnCommand")
                expect(Light is not None and TurnOnCommand is not None, "Command classes exist", "Define Light and TurnOnCommand")
                if Light and TurnOnCommand:
                    expect_equal(TurnOnCommand(Light()).execute(), "light:on", "Command delegates to receiver")
                finish("Good. The simple shape matters more than overengineering the example.")
                """,
            ),
        ),
    )


def state_lesson() -> Lesson:
    return Lesson(
        id="state-pattern",
        number=17,
        title="State Pattern",
        focus=("lifecycle behavior", "legal transitions", "state-specific rules"),
        overview="State becomes useful when behavior truly changes by lifecycle stage and the allowed transitions are part of the design problem.",
        patterns=("State",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "state-q1",
                "An order moves through `created -> paid -> packed -> shipped -> delivered`, and allowed operations vary by stage. Which pattern is strongest?",
                "easy",
                ("state", "workflow"),
                ("State", "Strategy", "Proxy", "Facade"),
                0,
                "The behavior depends on lifecycle state and legal transitions.",
            ),
            quiz(
                "state-q2",
                "What is the clearest difference between State and Strategy?",
                "medium",
                ("state", "strategy", "comparison"),
                (
                    "State models behavior tied to lifecycle transitions; Strategy is a pluggable algorithm choice.",
                    "Strategy always uses classes while State always uses enums.",
                    "State is structural while Strategy is behavioral.",
                    "They are equivalent as long as you use interfaces.",
                ),
                0,
                "That source-of-variation distinction is what interviewers are listening for.",
            ),
            code_task(
                "state-c1",
                "Implement `CreatedState.can_ship()` and `PaidState.can_ship()` for a tiny order lifecycle.",
                "easy",
                ("state", "workflow"),
                """
                class CreatedState:
                    def can_ship(self):
                        raise NotImplementedError

                class PaidState:
                    def can_ship(self):
                        raise NotImplementedError
                """,
                """
                class CreatedState:
                    def can_ship(self):
                        return False

                class PaidState:
                    def can_ship(self):
                        return True
                """,
                "The point is state-specific behavior, not a giant framework.",
                (
                    "Created state blocks shipping.",
                    "Paid state allows shipping.",
                ),
                """
                CreatedState = namespace.get("CreatedState")
                PaidState = namespace.get("PaidState")
                expect(CreatedState is not None and PaidState is not None, "State classes exist", "Define CreatedState and PaidState")
                if CreatedState and PaidState:
                    expect_equal(CreatedState().can_ship(), False, "Created state blocks shipping")
                    expect_equal(PaidState().can_ship(), True, "Paid state allows shipping")
                finish("Good. State patterns are about behavior that follows lifecycle.")
                """,
            ),
        ),
    )


def template_method_lesson() -> Lesson:
    return Lesson(
        id="template-method-pattern",
        number=18,
        title="Template Method Pattern",
        focus=("workflow skeleton", "customizable steps", "inheritance tradeoffs"),
        overview="Template Method is about keeping the broad sequence fixed while allowing narrow customization points.",
        patterns=("Template Method",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "template-q1",
                "Every ingestion pipeline follows `fetch -> validate -> transform -> persist -> emit metrics`, but validation and transformation differ by source. Which pattern fits best?",
                "medium",
                ("template-method", "workflow"),
                ("Template Method", "Strategy", "Memento", "Observer"),
                0,
                "The workflow skeleton is fixed; some steps vary.",
            ),
            quiz(
                "template-q2",
                "What is the main drawback of Template Method?",
                "medium",
                ("template-method", "tradeoffs"),
                (
                    "It always requires a database.",
                    "Inheritance-heavy templates get brittle when many axes of change appear.",
                    "It cannot express a fixed workflow.",
                    "It only works with exactly one hook method.",
                ),
                1,
                "Template Method works best when the skeleton is genuinely stable.",
            ),
            pitfall_task("template-method", "Template Method", "hard", ("Strategy", "Bridge", "Flyweight")),
        ),
    )


def iterator_lesson() -> Lesson:
    return Lesson(
        id="iterator-pattern",
        number=19,
        title="Iterator Pattern",
        focus=("traversal", "storage hiding", "paging", "generators"),
        overview="Iterator helps callers consume a sequence without caring how storage or paging works underneath.",
        patterns=("Iterator",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "iterator-q1",
                "A repository should let callers iterate search results without exposing whether data comes from memory or paginated remote fetches. Which pattern fits best?",
                "easy",
                ("iterator", "traversal"),
                ("Iterator", "Visitor", "Mediator", "Bridge"),
                0,
                "This is traversal over hidden representation.",
            ),
            quiz(
                "iterator-q2",
                "What is usually the most Pythonic way to implement Iterator behavior?",
                "easy",
                ("iterator", "python"),
                (
                    "A generator function yielding items in sequence.",
                    "A singleton class shared across all collections.",
                    "A facade class with one global list.",
                    "An adapter around every element.",
                ),
                0,
                "Generators are the usual Python answer unless you need a heavier object.",
            ),
            pitfall_task("iterator", "Iterator", "hard", ("Singleton", "Command", "Decorator")),
        ),
    )


def chain_lesson() -> Lesson:
    return Lesson(
        id="chain-pattern",
        number=20,
        title="Chain of Responsibility Pattern",
        focus=("fallthrough handlers", "escalation", "validation pipelines"),
        overview="Chain of Responsibility works when each handler gets a local chance to decide and then explicitly passes control onward.",
        patterns=("Chain of Responsibility",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "chain-q1",
                "A request should pass through handlers until one approves, rejects, or escalates it. Which pattern fits best?",
                "easy",
                ("chain-of-responsibility", "pipelines"),
                ("Chain of Responsibility", "Mediator", "Observer", "Interpreter"),
                0,
                "This is direct request fallthrough across handlers.",
            ),
            quiz(
                "chain-q2",
                "Which design smell often appears in a poor Chain of Responsibility?",
                "medium",
                ("chain-of-responsibility", "tradeoffs"),
                (
                    "The chain uses more than two classes.",
                    "Ownership is unclear and debugging who finally handled the request becomes painful.",
                    "The handlers return values.",
                    "A request can stop early.",
                ),
                1,
                "The danger is implicit, hard-to-debug ownership across a long chain.",
            ),
            code_task(
                "chain-c1",
                "Implement an escalation chain where L1 handles low, L2 handles medium, and Manager handles everything else.",
                "medium",
                ("chain-of-responsibility", "pipelines"),
                """
                class Handler:
                    def __init__(self, next_handler=None):
                        self.next_handler = next_handler

                    def handle(self, severity):
                        raise NotImplementedError

                class L1Support(Handler):
                    def handle(self, severity):
                        raise NotImplementedError

                class L2Support(Handler):
                    def handle(self, severity):
                        raise NotImplementedError

                class ManagerSupport(Handler):
                    def handle(self, severity):
                        raise NotImplementedError
                """,
                """
                class Handler:
                    def __init__(self, next_handler=None):
                        self.next_handler = next_handler

                    def handle(self, severity):
                        if self.next_handler:
                            return self.next_handler.handle(severity)
                        return None

                class L1Support(Handler):
                    def handle(self, severity):
                        if severity == "low":
                            return "l1"
                        return super().handle(severity)

                class L2Support(Handler):
                    def handle(self, severity):
                        if severity == "medium":
                            return "l2"
                        return super().handle(severity)

                class ManagerSupport(Handler):
                    def handle(self, severity):
                        return "manager"
                """,
                "Each handler decides locally, then falls through.",
                (
                    "Low is handled by L1.",
                    "Medium is handled by L2.",
                    "High reaches the manager.",
                ),
                """
                L1Support = namespace.get("L1Support")
                L2Support = namespace.get("L2Support")
                ManagerSupport = namespace.get("ManagerSupport")
                expect(all(item is not None for item in (L1Support, L2Support, ManagerSupport)), "Chain classes exist", "Keep the chain classes defined")
                if all(item is not None for item in (L1Support, L2Support, ManagerSupport)):
                    chain = L1Support(L2Support(ManagerSupport()))
                    expect_equal(chain.handle("low"), "l1", "Low severity handled by L1")
                    expect_equal(chain.handle("medium"), "l2", "Medium severity handled by L2")
                    expect_equal(chain.handle("high"), "manager", "High severity reaches manager")
                finish("Good. Chain should make fallthrough obvious, not magical.")
                """,
            ),
        ),
    )


def mediator_lesson() -> Lesson:
    return Lesson(
        id="mediator-pattern",
        number=21,
        title="Mediator Pattern",
        focus=("central coordination", "peer decoupling", "workflow ownership"),
        overview="Mediator is for systems where too many peers would otherwise talk directly to one another and coordination logic needs a home.",
        patterns=("Mediator",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "mediator-q1",
                "An interview scheduling system has Candidate, Interviewer, RoomCalendar, and ReminderService, and direct coordination is turning into a dependency mesh. Which pattern gives one coordination hub?",
                "medium",
                ("mediator", "coordination"),
                ("Mediator", "Observer", "Proxy", "Decorator"),
                0,
                "This is the classic many-peers, one-workflow-owner signal for Mediator.",
            ),
            quiz(
                "mediator-q2",
                "Why is Observer not the best default for this scheduling workflow?",
                "hard",
                ("mediator", "observer", "comparison"),
                (
                    "Observer is wrong because it uses callbacks.",
                    "Observer is one-way event fan-out; the scheduling case needs one place to own multi-party workflow decisions.",
                    "Observer only works for UI code.",
                    "Observer cannot coordinate more than two collaborators.",
                ),
                1,
                "Mediator is about workflow ownership, not just notifications.",
            ),
            pitfall_task("mediator", "Mediator", "hard", ("Observer", "Singleton", "Template Method")),
        ),
    )


def memento_lesson() -> Lesson:
    return Lesson(
        id="memento-pattern",
        number=22,
        title="Memento Pattern",
        focus=("snapshots", "undo", "state restoration", "encapsulation"),
        overview="Memento matters when state needs to be restored later without exposing every internal detail to the outside world.",
        patterns=("Memento",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "memento-q1",
                "A collaborative editor needs undo for draft text and formatting without exposing all document internals to outside callers. Which pattern fits best?",
                "medium",
                ("memento", "undo"),
                ("Memento", "Prototype", "Observer", "Command"),
                0,
                "Memento is built for safe snapshot-and-restore behavior.",
            ),
            quiz(
                "memento-q2",
                "What is the biggest practical warning with Memento?",
                "medium",
                ("memento", "tradeoffs"),
                (
                    "It only works for immutable objects.",
                    "Repeated snapshots of large mutable graphs can become expensive or leaky.",
                    "It cannot support undo.",
                    "It must always be paired with Visitor.",
                ),
                1,
                "Snapshot cost and encapsulation are the real design tension.",
            ),
            pitfall_task("memento", "Memento", "hard", ("Interpreter", "Bridge", "Factory Method")),
        ),
    )


def interpreter_lesson() -> Lesson:
    return Lesson(
        id="interpreter-pattern",
        number=23,
        title="Interpreter Pattern",
        focus=("tiny grammar", "rule trees", "mini DSLs"),
        overview="Interpreter is useful when the language is small enough that representing each expression node as an object stays readable.",
        patterns=("Interpreter",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "interpreter-q1",
                "You need a tiny rules engine supporting expressions like `tier == gold AND orders > 3`. Which pattern fits best?",
                "medium",
                ("interpreter", "rules"),
                ("Interpreter", "Visitor", "Facade", "Proxy"),
                0,
                "This is a mini grammar composed from expression objects.",
            ),
            quiz(
                "interpreter-q2",
                "When should you be careful with Interpreter?",
                "medium",
                ("interpreter", "tradeoffs"),
                (
                    "When the language is growing large or unbounded and the object model will explode.",
                    "When any expression needs recursion.",
                    "When conditions are evaluated against dictionaries.",
                    "When the implementation uses classes instead of functions.",
                ),
                0,
                "Interpreter is great for small grammars and brittle for huge ones.",
            ),
            code_task(
                "interpreter-c1",
                "Implement `Equals`, `GreaterThan`, and `And`, each exposing `evaluate(context)`.",
                "hard",
                ("interpreter", "rules"),
                """
                class Equals:
                    def __init__(self, field, value):
                        self.field = field
                        self.value = value

                    def evaluate(self, context):
                        raise NotImplementedError

                class GreaterThan:
                    def __init__(self, field, threshold):
                        self.field = field
                        self.threshold = threshold

                    def evaluate(self, context):
                        raise NotImplementedError

                class And:
                    def __init__(self, left, right):
                        self.left = left
                        self.right = right

                    def evaluate(self, context):
                        raise NotImplementedError
                """,
                """
                class Equals:
                    def __init__(self, field, value):
                        self.field = field
                        self.value = value

                    def evaluate(self, context):
                        return context.get(self.field) == self.value

                class GreaterThan:
                    def __init__(self, field, threshold):
                        self.field = field
                        self.threshold = threshold

                    def evaluate(self, context):
                        return context.get(self.field, 0) > self.threshold

                class And:
                    def __init__(self, left, right):
                        self.left = left
                        self.right = right

                    def evaluate(self, context):
                        return self.left.evaluate(context) and self.right.evaluate(context)
                """,
                "Leaf expressions inspect context; composite expressions delegate to children.",
                (
                    "Leaf expressions evaluate directly.",
                    "Composite expressions combine child evaluations.",
                ),
                """
                Equals = namespace.get("Equals")
                GreaterThan = namespace.get("GreaterThan")
                And = namespace.get("And")
                expect(all(item is not None for item in (Equals, GreaterThan, And)), "Interpreter classes exist", "Define Equals, GreaterThan, and And")
                if all(item is not None for item in (Equals, GreaterThan, And)):
                    rule = And(Equals("tier", "gold"), GreaterThan("orders", 3))
                    expect_equal(rule.evaluate({"tier": "gold", "orders": 4}), True, "Rule matches a valid context")
                    expect_equal(rule.evaluate({"tier": "gold", "orders": 1}), False, "Rule rejects low-order contexts")
                finish("Nice. For interview-sized DSLs, Interpreter can stay pleasantly small.")
                """,
            ),
        ),
    )


def visitor_lesson() -> Lesson:
    return Lesson(
        id="visitor-pattern",
        number=24,
        title="Visitor Pattern",
        focus=("stable structures", "growing operations", "analysis over trees"),
        overview="Visitor is a good fit when the data structure is stable but new operations keep arriving and you do not want to touch every node class each time.",
        patterns=("Visitor",),
        badge="Pattern Kit",
        tasks=(
            quiz(
                "visitor-q1",
                "An AST has stable node types like Literal, Add, and Multiply, but new analyses like pretty-printing and cost estimation keep arriving. Which pattern fits best?",
                "medium",
                ("visitor", "ast"),
                ("Visitor", "Iterator", "Decorator", "Mediator"),
                0,
                "The structure is stable and the operations keep growing.",
            ),
            quiz(
                "visitor-q2",
                "When does Visitor become painful?",
                "medium",
                ("visitor", "tradeoffs"),
                (
                    "When node types change frequently and every new node forces visitor updates everywhere.",
                    "When the structure is stable.",
                    "When there are several analyses to add.",
                    "When nodes are organized in a tree.",
                ),
                0,
                "Visitor optimizes for stable structure and changing operations, not the reverse.",
            ),
            pitfall_task("visitor", "Visitor", "hard", ("Command", "Proxy", "Builder")),
        ),
    )


def parking_lot_lab() -> Lesson:
    return Lesson(
        id="parking-lot-lab",
        number=25,
        title="Machine Coding Lab: Parking Lot",
        focus=("entities", "allocation policy", "spot selection", "extension points"),
        overview="Parking lot interviews are mostly about clean entities and policy boundaries. Do not cram every feature into one god class.",
        patterns=("Strategy", "Facade", "Observer"),
        badge="Lab",
        tasks=(
            quiz(
                "parking-q1",
                "If the interviewer later asks for nearest-spot, cheapest-spot, and EV-priority allocation, what is the cleanest extension point?",
                "hard",
                ("machine-coding", "strategy"),
                (
                    "Extract spot selection behind a strategy interface and keep the parking flow stable.",
                    "Make ParkingLot inherit one subclass per policy and switch classes at runtime.",
                    "Bake every policy into one large `park` method with flags.",
                    "Use a singleton so every policy sees the same state.",
                ),
                0,
                "Spot selection is a clean strategy axis.",
            ),
            code_task(
                "parking-c1",
                "Implement the in-memory parking lot. `park` picks the lexicographically smallest suitable free spot, `release` frees by vehicle number, and `available_spots` counts matching free spots.",
                "hard",
                ("machine-coding", "allocation"),
                """
                from dataclasses import dataclass

                FITS = {
                    "bike": {"bike", "car", "truck"},
                    "car": {"car", "truck"},
                    "truck": {"truck"},
                }

                @dataclass(frozen=True)
                class Spot:
                    id: str
                    kind: str

                @dataclass(frozen=True)
                class Ticket:
                    vehicle_number: str
                    vehicle_kind: str
                    spot_id: str

                class ParkingLot:
                    def __init__(self, spots):
                        self.spots = list(spots)
                        self.active = {}

                    def park(self, vehicle_number, vehicle_kind):
                        raise NotImplementedError

                    def release(self, vehicle_number):
                        raise NotImplementedError

                    def available_spots(self, vehicle_kind):
                        raise NotImplementedError
                """,
                """
                from dataclasses import dataclass

                FITS = {
                    "bike": {"bike", "car", "truck"},
                    "car": {"car", "truck"},
                    "truck": {"truck"},
                }

                @dataclass(frozen=True)
                class Spot:
                    id: str
                    kind: str

                @dataclass(frozen=True)
                class Ticket:
                    vehicle_number: str
                    vehicle_kind: str
                    spot_id: str

                class ParkingLot:
                    def __init__(self, spots):
                        self.spots = list(spots)
                        self.active = {}

                    def _free_spots(self):
                        occupied = {ticket.spot_id for ticket in self.active.values()}
                        return [spot for spot in self.spots if spot.id not in occupied]

                    def park(self, vehicle_number, vehicle_kind):
                        candidates = [spot for spot in self._free_spots() if spot.kind in FITS.get(vehicle_kind, set())]
                        if not candidates:
                            return None
                        chosen = sorted(candidates, key=lambda spot: spot.id)[0]
                        ticket = Ticket(vehicle_number, vehicle_kind, chosen.id)
                        self.active[vehicle_number] = ticket
                        return ticket

                    def release(self, vehicle_number):
                        ticket = self.active.pop(vehicle_number, None)
                        return ticket.spot_id if ticket else None

                    def available_spots(self, vehicle_kind):
                        return sum(1 for spot in self._free_spots() if spot.kind in FITS.get(vehicle_kind, set()))
                """,
                "Keep the state model tiny: spots, active tickets, and one allocation rule.",
                (
                    "Selects the smallest suitable free spot.",
                    "Tracks active tickets by vehicle number.",
                    "Release frees the spot and returns its id.",
                ),
                """
                Spot = namespace.get("Spot")
                ParkingLot = namespace.get("ParkingLot")
                expect(Spot is not None and ParkingLot is not None, "Parking lot classes exist", "Define Spot and ParkingLot")
                if Spot and ParkingLot:
                    lot = ParkingLot([Spot("A2", "car"), Spot("A1", "car"), Spot("B1", "truck")])
                    first = lot.park("KA-01", "bike")
                    expect(first is not None, "park returns a ticket when a spot exists", "park should return a ticket")
                    if first is not None:
                        expect_equal(first.spot_id, "A1", "Lot picks the lexicographically smallest suitable spot")
                    expect_equal(lot.available_spots("car"), 2, "Car availability counts remaining suitable spots")
                    second = lot.park("KA-02", "truck")
                    if second is not None:
                        expect_equal(second.spot_id, "B1", "Truck uses the truck spot")
                    expect_equal(lot.release("KA-01"), "A1", "release returns the freed spot id")
                finish("Solid. That is a clean baseline for later strategy and eventing extensions.")
                """,
            ),
            quiz(
                "parking-q2",
                "If entry and exit display boards are added next, what is the healthiest move?",
                "medium",
                ("machine-coding", "observer"),
                (
                    "Publish parking events so display boards subscribe and update without tangling spot-allocation logic.",
                    "Move parking logic into each display so the boards always have fresh state.",
                    "Let every board poll the entire lot on a timer from inside ParkingLot.",
                    "Replace the lot with a singleton and let boards read globals.",
                ),
                0,
                "This is a clean observer/eventing extension point.",
            ),
        ),
    )


def rate_limiter_lab() -> Lesson:
    return Lesson(
        id="rate-limiter-lab",
        number=26,
        title="Machine Coding Lab: Rate Limiter",
        focus=("windowing", "per-user state", "algorithm boundaries", "edge cases"),
        overview="Rate limiter interviews reward explicit state ownership and correct boundary handling much more than cleverness.",
        patterns=("Strategy", "State"),
        badge="Lab",
        tasks=(
            quiz(
                "limiter-q1",
                "What is the minimum state a fixed-window limiter needs per user to answer `allow(user_id, now)` correctly?",
                "hard",
                ("machine-coding", "rate-limiter"),
                (
                    "The current window identifier and the count inside that window.",
                    "Only the total number of requests ever seen for the user.",
                    "Every historical timestamp forever.",
                    "Just whether the last request succeeded.",
                ),
                0,
                "A fixed-window limiter only needs the active bucket id and count.",
            ),
            code_task(
                "limiter-c1",
                "Implement a per-user fixed-window limiter where `allow(user_id, now)` returns True only if the call fits within the current window.",
                "hard",
                ("machine-coding", "rate-limiter"),
                """
                class FixedWindowRateLimiter:
                    def __init__(self, limit, window_seconds):
                        self.limit = limit
                        self.window_seconds = window_seconds
                        self.windows = {}

                    def allow(self, user_id, now):
                        raise NotImplementedError
                """,
                """
                class FixedWindowRateLimiter:
                    def __init__(self, limit, window_seconds):
                        self.limit = limit
                        self.window_seconds = window_seconds
                        self.windows = {}

                    def allow(self, user_id, now):
                        window_id = now // self.window_seconds
                        active_window, count = self.windows.get(user_id, (window_id, 0))
                        if active_window != window_id:
                            active_window, count = window_id, 0
                        if count >= self.limit:
                            self.windows[user_id] = (active_window, count)
                            return False
                        count += 1
                        self.windows[user_id] = (active_window, count)
                        return True
                """,
                "Think in buckets, not giant histories.",
                (
                    "Tracks each user independently.",
                    "Resets when the window changes.",
                    "Denies requests beyond the per-window limit.",
                ),
                """
                Limiter = namespace.get("FixedWindowRateLimiter")
                expect(Limiter is not None, "FixedWindowRateLimiter exists", "Define FixedWindowRateLimiter")
                if Limiter is not None:
                    limiter = Limiter(2, 10)
                    expect_equal(limiter.allow("u1", 1), True, "First request is allowed")
                    expect_equal(limiter.allow("u1", 5), True, "Second request in window is allowed")
                    expect_equal(limiter.allow("u1", 9), False, "Third request in same window is denied")
                    expect_equal(limiter.allow("u1", 10), True, "Next window resets the count")
                finish("Good. The interview win here is correct window-boundary reasoning.")
                """,
            ),
            quiz(
                "limiter-q2",
                "If the interviewer later asks for sliding-window and token-bucket variants, what is the cleanest design move?",
                "medium",
                ("machine-coding", "strategy"),
                (
                    "Extract the limiting algorithm behind a strategy and keep the public limiter API stable.",
                    "Add more booleans to one monolithic limiter class.",
                    "Duplicate the whole limiter per algorithm.",
                    "Use a singleton so all algorithms share one state map.",
                ),
                0,
                "Algorithm choice is a strategy axis.",
            ),
        ),
    )


def notification_router_lab() -> Lesson:
    return Lesson(
        id="notification-router-lab",
        number=27,
        title="Machine Coding Lab: Notification Router",
        focus=("fallback order", "delivery attempts", "policy separation", "failure handling"),
        overview="Notification routing is a good interview problem because it mixes strategy, fallback, and observability without needing a huge domain model.",
        patterns=("Strategy", "Chain of Responsibility", "Facade"),
        badge="Lab",
        tasks=(
            quiz(
                "router-q1",
                "A notification has channel preferences like `['push', 'sms', 'email']`, and each channel may fail independently. What is the cleanest ownership boundary?",
                "hard",
                ("machine-coding", "routing"),
                (
                    "Keep the notification as data and route it through a dedicated router that owns fallback policy.",
                    "Make each notification subclass itself per preferred channel.",
                    "Put the entire fallback loop inside the Notification object.",
                    "Use Visitor so channels walk the notification graph.",
                ),
                0,
                "Fallback policy belongs in a router or strategy, not the data entity itself.",
            ),
            code_task(
                "router-c1",
                "Implement `NotificationRouter.route(notification)` so it tries channels in order and returns the first successful channel name, or `dead-letter` if all fail.",
                "hard",
                ("machine-coding", "routing"),
                """
                from dataclasses import dataclass

                @dataclass(frozen=True)
                class Notification:
                    user_id: str
                    body: str
                    channels: list[str]

                class Channel:
                    def __init__(self, name, sender):
                        self.name = name
                        self.sender = sender

                    def send(self, notification):
                        return self.sender(notification)

                class NotificationRouter:
                    def __init__(self, channels):
                        self.channels = {channel.name: channel for channel in channels}

                    def route(self, notification):
                        raise NotImplementedError
                """,
                """
                from dataclasses import dataclass

                @dataclass(frozen=True)
                class Notification:
                    user_id: str
                    body: str
                    channels: list[str]

                class Channel:
                    def __init__(self, name, sender):
                        self.name = name
                        self.sender = sender

                    def send(self, notification):
                        return self.sender(notification)

                class NotificationRouter:
                    def __init__(self, channels):
                        self.channels = {channel.name: channel for channel in channels}

                    def route(self, notification):
                        for name in notification.channels:
                            channel = self.channels.get(name)
                            if channel and channel.send(notification):
                                return name
                        return "dead-letter"
                """,
                "The router owns fallback order; channels only attempt delivery.",
                (
                    "Tries channels in order.",
                    "Stops at first success.",
                    "Falls back to dead-letter if all fail.",
                ),
                """
                Notification = namespace.get("Notification")
                Channel = namespace.get("Channel")
                Router = namespace.get("NotificationRouter")
                expect(all(item is not None for item in (Notification, Channel, Router)), "Router classes exist", "Define Notification, Channel, and NotificationRouter")
                if all(item is not None for item in (Notification, Channel, Router)):
                    push = Channel("push", lambda notification: False)
                    sms = Channel("sms", lambda notification: notification.user_id.startswith("vip"))
                    email = Channel("email", lambda notification: True)
                    router = Router([push, sms, email])
                    expect_equal(router.route(Notification("vip-7", "hi", ["push", "sms", "email"])), "sms", "Router falls through to first success")
                    expect_equal(router.route(Notification("user-2", "hi", ["push", "sms", "email"])), "email", "Router keeps trying later channels")
                    expect_equal(router.route(Notification("user-3", "hi", ["push"])), "dead-letter", "Router uses dead-letter when all fail")
                finish("Nice. That is a strong baseline for retries, priorities, and routing strategies.")
                """,
            ),
            quiz(
                "router-q2",
                "If premium users should prefer SMS before push while everyone else keeps the original order, what is the cleanest next move?",
                "medium",
                ("machine-coding", "strategy"),
                (
                    "Extract channel ordering behind a routing strategy while keeping delivery execution in the router.",
                    "Duplicate the router class for premium users.",
                    "Let every channel decide whether it should go first.",
                    "Move the logic into the Notification object.",
                ),
                0,
                "Channel ordering is another policy axis, so Strategy is the clean move.",
            ),
        ),
    )


LESSONS: tuple[Lesson, ...] = (
    solid_lesson(),
    singleton_lesson(),
    factory_method_lesson(),
    abstract_factory_lesson(),
    builder_lesson(),
    prototype_lesson(),
    adapter_lesson(),
    bridge_lesson(),
    composite_lesson(),
    decorator_lesson(),
    facade_lesson(),
    flyweight_lesson(),
    proxy_lesson(),
    strategy_lesson(),
    observer_lesson(),
    command_lesson(),
    state_lesson(),
    template_method_lesson(),
    iterator_lesson(),
    chain_lesson(),
    mediator_lesson(),
    memento_lesson(),
    interpreter_lesson(),
    visitor_lesson(),
    parking_lot_lab(),
    rate_limiter_lab(),
    notification_router_lab(),
)


LESSON_BY_ID = {lesson.id: lesson for lesson in LESSONS}


def lesson_index() -> list[dict[str, Any]]:
    return [
        {
            "id": lesson.id,
            "number": lesson.number,
            "title": lesson.title,
            "focus": list(lesson.focus),
            "taskCount": len(lesson.tasks),
            "patternCount": len(lesson.patterns),
            "badge": lesson.badge,
        }
        for lesson in LESSONS
    ]


def pattern_payload(name: str) -> dict[str, str]:
    pattern = PATTERN_LIBRARY[name]
    return {
        "name": pattern.name,
        "family": pattern.family,
        "intent": pattern.intent,
        "signals": pattern.signals,
        "pitfall": pattern.pitfall,
        "pythonTip": pattern.python_tip,
    }


def task_payload(task: Task) -> dict[str, Any]:
    payload = {
        "id": task.id,
        "kind": task.kind,
        "prompt": task.prompt,
        "difficulty": task.difficulty,
        "tags": list(task.tags),
        "hint": task.hint,
        "checklist": list(task.checklist),
    }
    if task.kind == "quiz":
        payload["options"] = list(task.options)
    else:
        payload["starter"] = task.starter
        payload["reference"] = task.solution
    return payload


def lesson_payload(lesson_id: str) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    return {
        "id": lesson.id,
        "number": lesson.number,
        "title": lesson.title,
        "focus": list(lesson.focus),
        "overview": lesson.overview,
        "badge": lesson.badge,
        "patterns": [pattern_payload(name) for name in lesson.patterns],
        "tasks": [task_payload(task) for task in lesson.tasks],
    }


def get_lesson(lesson_id: str) -> Lesson:
    if lesson_id in LESSON_BY_ID:
        return LESSON_BY_ID[lesson_id]
    return LESSONS[0]


def get_task(lesson: Lesson, task_id: str) -> Task:
    for task in lesson.tasks:
        if task.id == task_id:
            return task
    return lesson.tasks[0]


def run_python(lesson_id: str, task_id: str, code: str) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    task = get_task(lesson, task_id)
    if task.kind != "code":
        raise ValueError("Run is only available for coding tasks.")
    return execute_code(code)


def check_lld(
    lesson_id: str,
    task_id: str,
    *,
    answer: int | None = None,
    code: str | None = None,
) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    task = get_task(lesson, task_id)

    if task.kind == "quiz":
        if answer is None:
            raise ValueError("Choose an option first.")
        correct = answer == task.answer_index
        return {
            "correct": correct,
            "message": "Correct." if correct else "Not quite.",
            "explanation": task.explanation,
            "expectedIndex": task.answer_index,
            "solution": task.options[task.answer_index] if task.answer_index is not None else "",
        }

    if code is None:
        raise ValueError("Write Python before checking.")

    result = validate_code(code, task)
    result["solution"] = task.solution
    return result


def execute_code(code: str) -> dict[str, Any]:
    if not code.strip():
        raise ValueError("Write Python first.")
    completed = run_python_script(code)
    return {
        "ok": completed.returncode == 0,
        "message": "Executed successfully." if completed.returncode == 0 else "Execution failed.",
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "exitCode": completed.returncode,
    }


def validate_code(code: str, task: Task) -> dict[str, Any]:
    if not code.strip():
        raise ValueError("Write Python before checking.")
    script = build_validation_script(code, task.validator)
    completed = run_python_script(script)
    parsed = parse_validation_output(completed.stdout)
    user_stdout = "\n".join(
        line for line in completed.stdout.splitlines() if not line.startswith(RESULT_MARKER)
    ).strip()

    if parsed is None:
        message = completed.stderr.strip() or "Validation did not produce a result."
        return {
            "correct": False,
            "message": "Validation crashed.",
            "summary": message,
            "checks": [],
            "stdout": user_stdout,
            "stderr": completed.stderr.strip(),
        }

    parsed["message"] = "Solved." if parsed.get("correct") else "Not quite yet."
    parsed["stdout"] = user_stdout
    parsed["stderr"] = completed.stderr.strip()
    return parsed


def build_validation_script(code: str, validator: str) -> str:
    return "\n".join(
        [
            "import json",
            "",
            "namespace = {}",
            "",
            "try:",
            f"    exec(compile({code!r}, 'submission.py', 'exec'), namespace)",
            "except Exception as exc:",
            "    payload = {",
            "        'correct': False,",
            "        'summary': f'Execution failed before tests ran: {exc.__class__.__name__}: {exc}',",
            "        'checks': [],",
            "    }",
            f"    print('{RESULT_MARKER}' + json.dumps(payload))",
            "else:",
            textwrap.indent(VALIDATION_PREAMBLE, "    "),
            "    try:",
            textwrap.indent(validator, "        "),
            "    except Exception as exc:",
            "        payload = {",
            "            'correct': False,",
            "            'summary': f'Validator crashed: {exc.__class__.__name__}: {exc}',",
            "            'checks': checks if 'checks' in globals() else [],",
            "        }",
            f"        print('{RESULT_MARKER}' + json.dumps(payload))",
        ]
    )


def parse_validation_output(stdout: str) -> dict[str, Any] | None:
    for line in reversed(stdout.splitlines()):
        if line.startswith(RESULT_MARKER):
            return json.loads(line[len(RESULT_MARKER) :])
    return None


def run_python_script(script: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "submission.py"
        path.write_text(script, encoding="utf-8")
        try:
            return subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                timeout=EXEC_TIMEOUT_SECONDS,
                cwd=tmpdir,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = (exc.stdout or "").strip()
            stderr = ((exc.stderr or "").strip() + f"\nTimed out after {EXEC_TIMEOUT_SECONDS} seconds.").strip()
            return subprocess.CompletedProcess(
                args=[sys.executable, str(path)],
                returncode=124,
                stdout=stdout,
                stderr=stderr,
            )
