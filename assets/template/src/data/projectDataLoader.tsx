import React, { Component } from 'react';

class ProjectDataLoader extends Component {
  state = { data: null };

  componentDidMount() {
    console.log("componentDidMount");
    // Load your JSON data here
    fetch('project.nx')
      .then((response) => response.json())
      //.then((data) => this.setState({ data }))
      .then((data) => console.log(data));
  }

  render() {
  }
  
}

export default ProjectDataLoader;
