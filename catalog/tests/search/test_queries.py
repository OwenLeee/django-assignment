from django.test import TestCase

from catalog.models import Tag
from catalog.search.queries import search_products
from catalog.tests.models.helpers import create_category, create_product, create_tag


# AI Assisted
class ProductSearchQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.wire_category = create_category(name="Wire & Cable")
        cls.conduit_category = create_category(name="Conduit")
        cls.fittings_category = create_category(name="Fittings & Connectors")
        cls.commercial_tag = create_tag(name="Commercial")
        cls.industrial_tag = create_tag(name="Industrial")
        cls.indoor_tag = create_tag(name="Indoor")
        cls.outdoor_tag = create_tag(name="Outdoor")
        cls.prefab_tag = create_tag(name="Prefab Eligible")
        cls.van_stock_tag = create_tag(name="Van Stock")
        cls.mc_cable = create_product(
            name="MC Cable – 12/2",
            description="12/2 metal-clad cable for indoor commercial wiring and shop-prepared cable assemblies.",
            category=cls.wire_category,
        )
        cls.mc_cable.tags.add(cls.commercial_tag, cls.indoor_tag, cls.prefab_tag)
        cls.three_quarter_emt = create_product(
            name="3/4-inch EMT Conduit",
            description="3/4-inch EMT conduit for indoor commercial wire routing and prefabricated raceway sections.",
            category=cls.conduit_category,
        )
        cls.three_quarter_emt.tags.add(
            cls.indoor_tag, cls.commercial_tag, cls.prefab_tag
        )
        cls.one_inch_emt = create_product(
            name="1-inch EMT Conduit",
            description="1-inch EMT conduit for indoor industrial wire routing and shop-prepared raceway sections.",
            category=cls.conduit_category,
        )
        cls.one_inch_emt.tags.add(cls.indoor_tag, cls.industrial_tag, cls.prefab_tag)
        cls.pvc_conduit = create_product(
            name="3/4-inch PVC Conduit",
            description="3/4-inch PVC conduit for an outdoor commercial electrical raceway in this demo.",
            category=cls.conduit_category,
        )
        cls.pvc_conduit.tags.add(cls.outdoor_tag, cls.commercial_tag)
        cls.rigid_conduit = create_product(
            name="1-inch Rigid Steel Conduit",
            description="1-inch rigid steel conduit for industrial raceways and off-site assembly preparation.",
            category=cls.conduit_category,
        )
        cls.rigid_conduit.tags.add(cls.industrial_tag, cls.prefab_tag)
        cls.emt_coupling = create_product(
            name="3/4-inch EMT Coupling",
            description="3/4-inch EMT coupling for joining conduit sections in indoor commercial raceways.",
            category=cls.fittings_category,
        )
        cls.emt_coupling.tags.add(cls.indoor_tag, cls.commercial_tag, cls.van_stock_tag)

    def test_keyword_matches_description_only(self):
        cases = [
            (
                "INDOOR",
                [
                    self.mc_cable,
                    self.three_quarter_emt,
                    self.one_inch_emt,
                    self.emt_coupling,
                ],
            ),
            ("MC", []),  # MC appears only in the cable name, not in the description
        ]
        for keyword, expected in cases:
            with self.subTest(keyword=keyword):
                self.assertCountEqual(search_products(q=keyword), expected)

    def test_category_filters_products(self):
        self.assertCountEqual(
            search_products(category=self.conduit_category),
            [
                self.three_quarter_emt,
                self.one_inch_emt,
                self.pvc_conduit,
                self.rigid_conduit,
            ],
        )

    def test_combined_filters_apply_all_and_any_without_duplicates(self):
        tags = Tag.objects.filter(pk__in=[self.commercial_tag.pk, self.indoor_tag.pk])
        # PVC conduit misses the keyword; the coupling is in another category.
        # The 3/4-inch EMT conduit matches both tags and must appear only once.
        cases = [
            ("all", [self.three_quarter_emt]),
            ("any", [self.three_quarter_emt, self.one_inch_emt]),
        ]
        for mode, expected in cases:
            with self.subTest(mode=mode):
                results = search_products(
                    q="indoor", category=self.conduit_category, tags=tags, tag_mode=mode
                )
                self.assertCountEqual(results, expected)
        self.assertCountEqual(
            search_products(q="indoor", category=self.conduit_category, tags=tags),
            [self.three_quarter_emt],
        )

    def test_one_tag_matches_the_same_products_in_both_modes(self):
        tags = Tag.objects.filter(pk=self.commercial_tag.pk)
        cases = ["all", "any"]
        for mode in cases:
            with self.subTest(mode=mode):
                self.assertCountEqual(
                    search_products(tags=tags, tag_mode=mode),
                    [
                        self.mc_cable,
                        self.three_quarter_emt,
                        self.pvc_conduit,
                        self.emt_coupling,
                    ],
                )

    def test_no_tags_leave_other_filters_unchanged(self):
        cases = [
            (None, "all"),
            (None, "any"),
            (Tag.objects.none(), "all"),
            (Tag.objects.none(), "any"),
        ]
        for tags, mode in cases:
            with self.subTest(tags=tags, mode=mode):
                results = search_products(
                    q="conduit",
                    category=self.conduit_category,
                    tags=tags,
                    tag_mode=mode,
                )
                self.assertCountEqual(
                    results,
                    [
                        self.three_quarter_emt,
                        self.one_inch_emt,
                        self.pvc_conduit,
                        self.rigid_conduit,
                    ],
                )

    def test_no_matching_description_returns_no_products(self):
        self.assertCountEqual(search_products(q="nonexistent material"), [])

    def test_unfiltered_products_are_ordered_by_name_then_id(self):
        # Create a name tie to verify the ID ordering.
        later_emt = create_product(
            name=self.three_quarter_emt.name,
            description=self.three_quarter_emt.description,
            category=self.conduit_category,
        )
        later_emt.tags.add(*self.three_quarter_emt.tags.all())
        self.assertEqual(
            list(search_products()),
            [
                self.one_inch_emt,
                self.rigid_conduit,
                self.three_quarter_emt,
                later_emt,
                self.emt_coupling,
                self.pvc_conduit,
                self.mc_cable,
            ],
        )
