function doGet(e) {
  const userEmail = Session.getActiveUser().getEmail();
  if (!userEmail) {
    return HtmlService.createHtmlOutput('<h1>Please log in to view this page.</h1>');
  }

  const config = getConfig_();
  const template = HtmlService.createTemplateFromFile('index');
  template.config = config;
  template.user = userEmail;
  
  return template.evaluate()
      .setTitle('Saga Configuration')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}