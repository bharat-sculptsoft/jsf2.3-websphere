package com;

import java.io.Serializable;

import javax.enterprise.context.RequestScoped;
import javax.faces.application.FacesMessage;
import javax.faces.context.FacesContext;
import javax.inject.Named;

@Named
@RequestScoped
public class IndexBean implements Serializable {

	private String name;

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String save() {
		System.out.println("inside save()");
		FacesContext.getCurrentInstance().addMessage(null, new FacesMessage(name + " welcome to webshpere with jsf 2.3"));
		return "";
	}

}