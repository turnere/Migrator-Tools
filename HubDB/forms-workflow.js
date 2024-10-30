const hubspot = require('@hubspot/api-client');

exports.main = (event, callback) => {
  // Instantiate HubSpot API Client
  const hubspotClient = new hubspot.Client({
    accessToken: process.env.secretName
  });

  // Get the contact ID from the workflow event
  const contactId = event.object.objectId;

  // Step 1: Get engagements (including form submissions) for the contact
  hubspotClient.crm.engagements.getAll({
    objectId: contactId
  })
  .then(engagements => {
    if (!engagements.body.results || engagements.body.results.length === 0) {
      console.log('No engagements found for this contact');
      throw new Error('No engagements found');
    }

    // Assuming the most recent engagement is the form submission
    const lastFormSubmission = engagements.body.results.find(engagement => engagement.engagement.type === 'FORM_SUBMISSION');
    
    if (!lastFormSubmission) {
      console.log('No form submission found for this contact');
      throw new Error('No form submission found');
    }

    const formId = lastFormSubmission.engagement.id; // Adjust this based on actual response

    console.log(`Found form ID: ${formId}`);

    // Step 2: Query the HubDB table for a row matching the form ID
    const hubdbTableId = '29947477'; // Replace with your HubDB table ID

    hubspotClient.cms.hubdb.rowsApi.getTableRows(hubdbTableId)
    .then(searchResult => {
      let rows = searchResult.body.results;

      if (rows.length === 0) {
        console.log('No rows found in HubDB');
        throw new Error('No matching HubDB row');
      }

      // Manually filter rows to find the one with the matching form ID
      const matchingRow = rows.find(row => row.values['form_id_column_name'] === formId); // Adjust with your column name

      if (!matchingRow) {
        console.log('No matching row in HubDB for the form ID');
        throw new Error('No matching HubDB row');
      }

      const relevantColumnData = matchingRow.values['column_name'];  // Replace with your actual column name
      console.log(`Found data from HubDB: ${relevantColumnData}`);

      // Step 3: Return the data in output fields for further workflow actions
      callback({
        outputFields: {
          email: event.inputFields['email'],
          phone: event.inputFields['phone'],
          hubdb_column_data: relevantColumnData
        }
      });
    })
    .catch(error => {
      console.log(`Error querying HubDB: ${error.message}`);
      throw new Error('Error querying HubDB');
    });
  })
  .catch(error => {
    console.log(`Error retrieving engagements: ${error.message}`);
    throw new Error('Error retrieving engagements');
  });
}
