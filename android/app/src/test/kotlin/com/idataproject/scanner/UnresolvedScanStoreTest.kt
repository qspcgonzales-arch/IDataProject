package com.idataproject.scanner

import org.junit.Test
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue

/**
 * Unit tests for UnresolvedScanStore.
 *
 * Requires Robolectric (or an instrumented/androidTest run) to provide
 * a Context and a real SQLite database — these are written against
 * that expectation, matching how this module's other Android tests
 * are structured as scaffolds pending the test runner setup task.
 */
class UnresolvedScanStoreTest {

    @Test
    fun testLogUnresolvedPersistsEpc() {
        // TODO: val store = UnresolvedScanStore(context)
        // store.logUnresolved("E28011700000021500000099")
        // TODO: assertEquals(1, store.countPendingReview())
    }

    @Test
    fun testUnresolvedEpcNeverSilentlyDropped() {
        // Regression test for the gap the Section 9 addendum reintroduced:
        // an EPC with no matching stock.lot must still be recorded
        // somewhere for operator review, not discarded.
        // TODO: val store = UnresolvedScanStore(context)
        // store.logUnresolved("E28011700000021500000098")
        // val pending = store.getPendingReview()
        // TODO: assertTrue(pending.any { it.epc == "E28011700000021500000098" })
    }

    @Test
    fun testMarkResolvedRemovesFromPendingReview() {
        // TODO: val store = UnresolvedScanStore(context)
        // val id = store.logUnresolved("E28011700000021500000097")
        // store.markResolved(id)
        // TODO: assertEquals(0, store.countPendingReview())
    }

    @Test
    fun testDuplicateUnresolvedScansAllLogged() {
        // Same EPC failing repeatedly should record every attempt,
        // not just the first — helps an operator see a tag that
        // consistently fails to resolve.
        // TODO: val store = UnresolvedScanStore(context)
        // store.logUnresolved("E28011700000021500000096")
        // store.logUnresolved("E28011700000021500000096")
        // TODO: assertEquals(2, store.countPendingReview())
    }
}
