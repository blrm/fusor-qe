from lib.deployment_runner import UIDeploymentRunner
from pages.wizard.rhev.setup_type import SetupType
from pages.wizard.rhev.engine import Engine
from pages.wizard.cloudforms.installation_location import InstallationLocation
from pages.wizard.subscriptions.content_provider import ContentProviderPage
from pages.wizard.subscriptions.review_subscriptions import ReviewSubscriptions
from pages.wizard.review.installation_progress import InstallationProgress


def test_e2e_deployment(new_deployment_pg, variables):
    '''
    Using values from the provided variables file to run a QCI deployment

    This test case mostly handles the logic that determines which page
    we are one and how to proceed through the wizard based on that. The actual
    actions performed on each page and the yaml values that direct those
    actions are handled by the UIDeploymentRunner class.
    '''
    runner = UIDeploymentRunner()
    deployment_name_pg = runner.product_selection(new_deployment_pg)
    update_avail_pg = runner.deployment_name(deployment_name_pg)
    insights_pg = runner.update_availability(update_avail_pg)
    next_pg = runner.access_insights(insights_pg)
    # check if we are on the RHV Setup Type page
    if isinstance(next_pg, SetupType):
        setuptype_pg = next_pg
        rhv_hosts_pg = runner.setup_type(setuptype_pg)
        # check if this is a engine + hypervisor deployment
        if isinstance(rhv_hosts_pg, Engine):
            rhv_hyper_pg = runner.engine(rhv_hosts_pg)
        else:
            rhv_hyper_pg = rhv_hosts_pg
        rhv_config_pg = runner.hypervisor(rhv_hyper_pg)
        rhv_storage_pg = runner.rhv_configuration(rhv_config_pg)
        next_pg = runner.rhv_storage(rhv_storage_pg)
    # check if we are on the CFME install location page)
    if isinstance(next_pg, InstallationLocation):
        cfmeinstall_pg = next_pg
        cfmeconfig_pg = runner.cfme_install(cfmeinstall_pg)
        next_pg = runner.cfme_config(cfmeconfig_pg)
    # check if we are at the Content Provider Page
    if isinstance(next_pg, ContentProviderPage):
        contentprov_pg = next_pg
        sma_pg = runner.content_provider(contentprov_pg)
        add_subs_pg = runner.subscription_management(sma_pg)
        next_pg = runner.add_subscriptions(add_subs_pg)
    # check if we are at Review Subscriptions page
    # this handles the case where a manifest is already attached
    # and the subscriptions pages in the wizard are skipped
    # TODO: this will need to be revisited once the deployment_step_bar
    # has been updated to handle this situation
    if isinstance(next_pg, ReviewSubscriptions):
        review_subs_pg = next_pg
        review_dep_pg = runner.review_subscriptions(review_subs_pg)
        progress_pg = runner.installation_review(review_dep_pg)
        # TODO test that deployment completes via API
        #
        # This just asserts that we have made it to the deployment progress
        # page successfully. To match the functionality of the existing
        # robottelo test, the API will need to track the progress of the
        # deployment from here.
        assert isinstance(progress_pg, InstallationProgress)
    else:
        # if we aren't at the Review Subscriptions page, something went wrong.
        assert False
